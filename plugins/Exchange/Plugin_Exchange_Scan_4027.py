import urllib3
from ldap3 import SUBTREE, LEVEL, BASE
from copy import copy
from plugins.Exchange import PluginExchangeScanBase
from utils.consts import AllPluginTypes

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PluginExchang(PluginExchangeScanBase):
    """POP3的登录认证类型安全登录未启用"""

    display = "POP3的登录认证类型安全登录未启用"
    alias = "ex_no_enable_pop3_login_auth"
    p_type = AllPluginTypes.Scan

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_script(self, args) -> dict:

        result = copy(self.result)
        instance_list = []
        query = "(objectClass=*)"
        attributes = ["cn"]
        ldap_cli = "CN=Microsoft Exchange,CN=Services,CN=Configuration," + self.ldap_cli.domain_dn
        entry_generator = self.ldap_cli.con.extend.standard.paged_search(search_base=ldap_cli,
                                                                         search_filter=query,
                                                                         search_scope=LEVEL,
                                                                         get_operational_attributes=True,
                                                                         attributes=attributes,
                                                                         paged_size=1000,
                                                                         generator=True)

        for entry in entry_generator:
            ldap_cli1 = "CN=Administrative Groups,CN=" + entry["attributes"]['cn'] + "," + ldap_cli
            entry_generator1 = self.ldap_cli.con.extend.standard.paged_search(search_base=ldap_cli1,
                                                                              search_filter=query,
                                                                              search_scope=LEVEL,
                                                                              get_operational_attributes=True,
                                                                              attributes=attributes,
                                                                              paged_size=1000,
                                                                              generator=True)
            for entry1 in entry_generator1:
                ldap_cli12 = "CN=Servers,CN=" + entry1["attributes"]['cn'] + "," + ldap_cli1

                attributes = ["cn"]
                entry_generator2 = self.ldap_cli.con.extend.standard.paged_search(search_base=ldap_cli12,
                                                                                  search_filter=query,
                                                                                  search_scope=LEVEL,
                                                                                  get_operational_attributes=True,
                                                                                  attributes=attributes,
                                                                                  paged_size=1000,
                                                                                  generator=True)
                for entry2 in entry_generator2:
                    attributes = ["msExchAuthenticationFlags", "cn"]
                    ldap_cli3 = "CN=1,CN=POP3,CN=Protocols,CN=" + entry2["attributes"]['cn'] + "," + ldap_cli12
                    entry_generator3 = self.ldap_cli.con.extend.standard.paged_search(search_base=ldap_cli3,
                                                                                      search_filter=query,
                                                                                      search_scope=BASE,
                                                                                      get_operational_attributes=True,
                                                                                      attributes=attributes,
                                                                                      paged_size=1000,
                                                                                      generator=True)
                    for entry3 in entry_generator3:
                        if entry3["attributes"]['msExchAuthenticationFlags']:
                            result['status'] = 1
                            instance = {}
                            instance["账户名"] = entry3["attributes"]['cn']
                            instance_list.append(instance)
        result['data'] = {"instance_list": instance_list}
        return result
