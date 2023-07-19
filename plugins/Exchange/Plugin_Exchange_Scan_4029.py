import urllib3
from ldap3 import SUBTREE, LEVEL, BASE
from copy import copy
from plugins.Exchange import PluginExchangeScanBase
from utils.consts import AllPluginTypes

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PluginExchangeInvalidPwdValidityPeriod(PluginExchangeScanBase):
    """密码有效期设置不合理"""

    display = "密码有效期设置不合理"
    alias = "ex_inv_pwd_period"
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

        for entry1 in entry_generator:
            ldap_cli1 = "CN=Default,CN=Mobile Mailbox Policies,CN=" + entry1["attributes"]['cn'] + "," + ldap_cli

            attributes = ["msExchMobileDevicePasswordExpiration", "cn"]
            entry_generator2 = self.ldap_cli.con.extend.standard.paged_search(search_base=ldap_cli1,
                                                                              search_filter=query,
                                                                              search_scope=BASE,
                                                                              get_operational_attributes=True,
                                                                              attributes=attributes,
                                                                              paged_size=1000,
                                                                              generator=True)
            for entry2 in entry_generator2:

                if not entry2["attributes"]['msExchMobileDevicePasswordExpiration'] or entry2["attributes"]['msExchMobileDevicePasswordExpiration'] > 7776000:
                    result['status'] = 1
                    instance ={}
                    instance["密码有效期"] = entry2["attributes"]['cn']
                    instance_list.append(instance)
        result['data'] = {"instance_list": instance_list}
        return result
