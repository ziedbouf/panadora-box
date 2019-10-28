import os
import time
import uuid
import yaml
import copy
import shlex
import shutil
import logging
import subprocess
import ipaddress

from pandora.config import current_config

logger = logging.getLogger('pandora_api')
config = current_config()


class Kubespray:
    """Kubespray wrapper.
    This approach is not scalable. It may be solved by storing ssh
    keys in db and running ansible on the one of the master nodes.
    :param str cluster_id:
    :param str ssh_username:
    :param str clusters_path:
    :param str kubespray_path:
    :param dict os_kwargs:
    """

    def __init__(self, *, cluster_id, ssh_username,
                 clusters_path, kubespray_path, os_kwargs):
        self.cluster_id = cluster_id
        self.ssh_username = ssh_username
        self.clusters_path = clusters_path
        self.kubespray_path = kubespray_path
        self.os_kwargs = os_kwargs
        self.ssh_common_args = ("-o", "UserKnownHostsFile=/dev/null",
                                "-o", "StrictHostKeyChecking=no",
                                "-i", os.path.join(clusters_path, "ssh_key"))
        self._make_files_dir()

    def deploy(self, cluster_metadata):
        resources = cluster_metadata['resources']
        inventory = self._generate_inventory(resources)
        self._save_inventory(inventory, "hosts.json")
        self._create_group_vars(cluster_metadata)
        self._wait_for_ping()
        self._run_ansible()
        return self._get_kubeconfig(resources["masters"][0]["fip"])

    def scale(self, resources):
        inventory = self._generate_inventory(resources)
        self._save_inventory(inventory, "hosts.json")
        self._wait_for_ping()
        self._run_ansible(playbook="scale.yml")

    def shrink(self, resources, *, new_slave_count):
        hostnames = [s["hostname"] for s in resources["slaves"]]
        hostnames.sort()
        slaves_left = hostnames[:new_slave_count]
        inv = self._generate_inventory(resources, keep_slaves=slaves_left)
        self._save_inventory(inv, "remove.json")
        self._run_ansible(playbook="remove-node.yml", inventory="remove.json")
        return hostnames[new_slave_count:]

    def delete(self):
        shutil.rmtree(self._get_cluster_path())

    def _save_inventory(self, inventory, filename):
        with open(self._get_cluster_path(filename), "w") as fp:
            json.dump(inventory, fp, indent=4)

    def _create_group_vars(self, metadata):
        src = os.path.join(self.kubespray_path, "inventory/sample/group_vars")
        dst = self._get_cluster_path("group_vars")
        shutil.copytree(src, dst)

        persistent_volumes = metadata.get("persistent_volume")
        kubespray_vars = {
            "persistent_volumes_enabled": True} if persistent_volumes else {}

        kubespray_vars["cloud_provider"] = "openstack"
        kubespray_vars["openstack_blockstorage_version"] = config.get(
            "KS_OS_BLOCKSTORAGE_VERSION") or "v2"
        kubespray_vars["calico_endpoint_to_host_action"] = "ACCEPT"
        if config.get("KS_NO_PROXY"):
            kubespray_vars["no_proxy"] = config.KS_NO_PROXY

        kubespray_vars["openstack_lbaas_subnet_id"] = metadata["resources"]["subnet_id"]
        kubespray_vars["openstack_lbaas_floating_network_id"] = metadata["resources"]["ext_net_id"]
        # See https://github.com/kubernetes-incubator/kubespray/issues/2141
        # Set this variable to true to get rid of this issue
        kubespray_vars["volume_cross_zone_attachment"] = True

        # See https://github.com/kubernetes-incubator/kubespray/issues/1430
        # Set all fips in this var to get rid of kubectl ssl-certs issue
        ssl_fips = [master["fip"]
                    for master in metadata["resources"]["masters"]]
        if ssl_fips:
            kubespray_vars["supplementary_addresses_in_ssl_keys"] = ssl_fips

        image_var_names = [var_name for var_name in dir(
            config) if var_name.endswith(('_IMAGE_REPO', '_IMAGE_TAG'))]
        image_variables = {k.lower(): getattr(config, k)
                           for k in image_var_names}
        kubespray_vars.update(image_variables)
        with open(os.path.join(dst, "k8s-cluster.yml"), "a") as k8s_yaml:
            yaml.dump(kubespray_vars, k8s_yaml, default_flow_style=False)

    def _make_files_dir(self):
        os.makedirs(self._get_cluster_path(), exist_ok=True)

    def _generate_inventory(self, resources, keep_slaves=None):
        """Generate inventory object for kubespray.
        :param list keep_slaves: list of slaves to keep when generating
                                 inventory for removing nodes (see link below)
        https://github.com/kubernetes-incubator/kubespray/blob/v2.5.0/docs/getting-started.md#remove-nodes
        :param dict resources: dict with masters and slaves details
        Resources may look like this:
        {
            "masters": [
                {"hostname": "host-1", "ip": "10.1.1.1", "fip": "172.16.1.1"},
                {"hostname": "host-2", "ip": "10.1.1.2", "fip": "172.16.1.2"},
                {"hostname": "host-3", "ip": "10.1.1.3", "fip": "172.16.1.3"},
            ],
            "slaves": [
                {"hostname": "host-4", "ip": "10.1.1.4"},
                {"hostname": "host-5", "ip": "10.1.1.5"},
            ],
        }
        Return value is json serializable object to be used as kubespray
        inventory file.
        """
        keep_slaves = keep_slaves or []
        ssh_common_args = " ".join(self.ssh_common_args)
        conf = {
            "all": {"hosts": {}},
            "kube-master": {
                "hosts": {},
                "vars": {
                    "ansible_ssh_common_args": ssh_common_args
                },
            },
            "kube-node": {"hosts": {}},
            "keep-slaves": {"hosts": {}},
            "etcd": {"hosts": {}},
            "vault": {"hosts": {}},
            "k8s-cluster": {"children": {"kube-node": None,
                                         "kube-master": None}},
        }
        for master in resources["masters"]:
            conf["all"]["hosts"][master["hostname"]] = {
                "access_ip": master["ip"],
                "ansible_host": master["fip"],
                "ansible_user": self.ssh_username,
                "ansible_become": True,
            }
            conf["kube-master"]["hosts"][master["hostname"]] = None
            conf["etcd"]["hosts"][master["hostname"]] = None
            conf["vault"]["hosts"][master["hostname"]] = None
        for slave in resources["slaves"]:
            conf["all"]["hosts"][slave["hostname"]] = {
                "ansible_host": slave["ip"],
                "ansible_user": self.ssh_username,
                "ansible_become": True,
            }
            if slave["hostname"] not in keep_slaves:
                conf["kube-node"]["hosts"][slave["hostname"]] = None

        user = shlex.quote(self.ssh_username)
        ip = shlex.quote(resources["masters"][0]["fip"])
        ssh_args_fmt = "-o ProxyCommand=\"ssh {user}@{ip} {args} -W %h:%p\" {args}"
        ssh_args = ssh_args_fmt.format(user=user, ip=ip,
                                       args=ssh_common_args)
        conf["kube-node"]["vars"] = {"ansible_ssh_common_args": ssh_args}
        conf["keep-slaves"]["vars"] = {"ansible_ssh_common_args": ssh_args}
        return conf

    def _get_cluster_path(self, *args):
        return os.path.join(self.clusters_path, self.cluster_id, *args)

    def _wait_for_ping(self, retries=15, sleep=10):
        args = [config.KS_ANSIBLE_CMD, "-m",
                "ping", "all", "-i", "hosts.json", "-e", "ansible_python_interpreter=/usr/bin/python3"]
        while retries:
            retries -= 1
            time.sleep(sleep)
            cp = subprocess.run(args, cwd=self._get_cluster_path())
            if cp.returncode == 0:
                return
        raise RuntimeError("At least one node is unreachable")

    def _construct_env(self):
        env = os.environ.copy()
        env.update({
            "OS_PROJECT_ID": self.os_kwargs["project_id"],
            "OS_TENANT_ID": self.os_kwargs["project_id"],
            "OS_REGION_NAME": self.os_kwargs["region_name"],
            "OS_USER_DOMAIN_NAME": self.os_kwargs["domain_name"],
            "OS_PROJECT_NAME": self.os_kwargs["project_id"],
            "OS_PASSWORD": self.os_kwargs["password"],
            "OS_AUTH_URL": self.os_kwargs["auth_url"],
            "OS_USERNAME": self.os_kwargs["username"],
            "OS_INTERFACE": self.os_kwargs["identity_interface"],
        })
        return env

    def _run_ansible(self, inventory="hosts.json", playbook="cluster.yml"):
        inventory = self._get_cluster_path(inventory)
        args = [
            config.KS_ANSIBLE_PLAYBOOK_CMD, "-b", "-i",
            inventory, playbook,
            "-e", "delete_nodes_confirmation=yes",
            "-e", "docker_dns_servers_strict=no",
            "-e", "ansible_python_interpreter=/usr/bin/python3"
        ]
        env = self._construct_env()
        self.ansible_log = os.path.join(self._get_cluster_path(
        ), "ansible_log_for_{0}_playbook.txt".format(playbook))
        with open(self.ansible_log, "a+") as log_file:
            pipe = subprocess.Popen(
                args,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=self.kubespray_path,
                env=env,
            )
            pipe.wait()
        if pipe.returncode:
            with open(self.ansible_log, "r") as log_file:
                result = log_file.read()
            if result.find("fatal:"):
                raise RuntimeError(
                    "Ansible command execution failed ({})".format(" ".join(args)))

    def _get_kubeconfig(self, ip):
        cat_kubeconf = "sudo cat /etc/kubernetes/admin.conf"
        host = "@".join((self.ssh_username, ip))
        args = ("ssh", host) + self.ssh_common_args + (cat_kubeconf,)
        kubeconfig = yaml.safe_load(subprocess.check_output(args))
        kubeconfig["clusters"][0]["cluster"]["server"] = "https://%s:6443" % ip
        return kubeconfig

    def get_ssh_key(self):
        """Generate ssh keypair if not exist.
        Return public key as string.
        """
        os.makedirs(config.KS_FILES_PATH, exist_ok=True)
        ssh_key_path = os.path.join(config.KS_FILES_PATH, "ssh_key")
        if not os.path.exists(ssh_key_path):
            cmd = [config.KS_SSH_KEYGEN_CMD, "-P", "", "-f", ssh_key_path]
            subprocess.check_call(cmd)
        with open(ssh_key_path + ".pub", "r") as key_file:
            return key_file.read()
