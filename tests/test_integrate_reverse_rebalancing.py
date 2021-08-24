import subprocess

from .test_integrate_base_rebalancing import BalancedTestBaseRebalancing
from .stories.rebalancing_stories import REVERSE_REBALANCING_STORIES
from iconservice import *
from iconsdk.wallet.wallet import KeyWallet


class BalancedTestLiquidation(BalancedTestBaseRebalancing):

    def patch_constants(self, current, replace_with):
        read_lines = 'data_bytes_sicx = b\'{"method": "_swap", "params": {"toToken": "' + current + '"}}\'\n'
        with open("core_contracts/rebalancing/rebalancing.py") as file:
            file_lines = file.readlines()

        if read_lines not in file_lines:
            raise
        file_lines = [i
                      if i != read_lines
                      else read_lines.replace(current, replace_with)
                      for i in file_lines]
        with open("core_contracts/rebalancing/rebalancing.py", "w") as file:
            file_lines = file.writelines(file_lines)

    def setUp(self):
        super().setUp()
        sicx = self.get_sicx_address()

        current_sicx_address = "cx2609b924e33ef00b648a409245c7ea394c467824"
        new_sicx_address = sicx
        self.patch_constants(current_sicx_address, new_sicx_address)

    def tearDown(self):
        sicx = self.get_sicx_address()

        current_sicx_address = sicx
        new_sicx_address = "cx2609b924e33ef00b648a409245c7ea394c467824"
        self.patch_constants(current_sicx_address, new_sicx_address)

    def setAddresses(self):

        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setRebalancing',
                     {"_address": self.contracts['rebalancing']})
        self.send_tx(self.btest_wallet, self.contracts['rebalancing'], 0, 'setGovernance',
                     {"_address": self.contracts['governance']})

        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'rebalancingSetSicx',
                     {"_address": self.contracts['sicx']})
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'rebalancingSetBnusd',
                     {"_address": self.contracts['bnUSD']})
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'rebalancingSetLoans',
                     {"_address": self.contracts['loans']})
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'rebalancingSetDex',
                     {"_address": self.contracts['dex']})

        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setLoansRebalance',
                     {"_address": self.contracts['rebalancing']})
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setLoansDex',
                     {"_address": self.contracts['dex']})

        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setRebalancingSicx',
                     {"_value": 1000 * 10 ** 18})

        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setRebalancingThreshold',
                     {"_value": 5 * 10 ** 17})
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, 'setRebalancingBnusdValue',
                     {"_value": 1000 * 10 ** 18})

    def test_reverse_rebalance(self):
        self.score_update("rebalancing")
        test_cases = REVERSE_REBALANCING_STORIES
        self.send_tx(self._test1, self.contracts['loans'], 10000 * 10 ** 18, 'depositAndBorrow',
                     {'_asset': 'bnUSD', '_amount': 2000 * 10 ** 18})
        self.send_tx(self.btest_wallet, self.contracts['staking'], 500000 * 10 ** 18, 'stakeICX',
                     {"_to": self._test1.get_address()})
        self.send_tx(self._test1, self.contracts['bnUSD'], 0, 'transfer',
                     {'_to': self.contracts['rebalancing'], '_value': 1000*10**18})

        self.setAddresses()
        wallets = []

        for i in range(5):
            wallets.append(KeyWallet.create())

        for i in range(5):
            self.send_icx(self.btest_wallet, wallets[i].get_address(), 2500 * 10 ** 18)

        for i in range(5):
            self.send_tx(wallets[i], self.contracts['loans'], 1000 * 10 ** 18, 'depositAndBorrow',
                         {'_asset': 'bnUSD', '_amount': 100 * 10 ** 18})

        self.send_icx(self.btest_wallet, self.user1.get_address(), 2500 * 10 ** 18)
        self.send_icx(self.btest_wallet, self.user2.get_address(), 2500 * 10 ** 18)
        self.send_tx(self.user1, self.contracts['loans'], 1000 * 10 ** 18, 'depositAndBorrow',
                     {'_asset': 'bnUSD', '_amount': 100 * 10 ** 18})
        self.send_tx(self.user2, self.contracts['loans'], 2000 * 10 ** 18, 'depositAndBorrow',
                     {'_asset': 'bnUSD', '_amount': 200 * 10 ** 18})

        for case in test_cases['stories']:
            print("############################################################################################")
            print(case['description'])

            res = self.call_tx(self.contracts['bnUSD'], 'balanceOf', {"_owner": self.contracts['rebalancing']})
            self.assertEqual(int(res, 0), case['actions']['initial_bnUSD_in_rebalancer'])

            self.call_tx(self.contracts['dex'], 'getPoolStats', {"_id": 2})

            dat = "{\"method\": \"_swap\", \"params\": {\"toToken\": \""+self.contracts['bnUSD']+"\"}}"
            data = dat.encode("utf-8")
            self.send_tx(self._test1, self.contracts['sicx'], 0, case['actions']['method'],
                         {'_to': self.contracts['dex'], '_value': case['actions']['amount'], "_data": data})

            self.call_tx(self.contracts['dex'], 'getPoolStats', {"_id": 2})

            status = self.call_tx(self.contracts['rebalancing'], 'getRebalancingStatus', {})
            self.assertEqual(int(status[2], 0), case['actions']['rebalancing_status'])

            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self._test1.get_address()})
            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self.user1.get_address()})
            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self.user2.get_address()})
            # account positions after rebalancing
            before = {}
            wallet_dict = {}
            for i in range(len(wallets)):
                wallet_dict = {"user1": self.user1.get_address(), "user2": self.user2.get_address(),
                               "user3": self._test1.get_address(), "user4": wallets[i].get_address(),
                               "user5": wallets[i].get_address(), "user6": wallets[i].get_address(),
                               "user7": wallets[i].get_address(), "user8": wallets[i].get_address()}
            for key, value in wallet_dict.items():
                before[key] = self.get_account_position(value)

            rebabalce = self.send_tx(self.btest_wallet, self.contracts['rebalancing'], 0, 'rebalance', {})

            event = (rebabalce['eventLogs'])
            redeemed_bnusd = ""
            sum = 0
            for i in event:
                res = (i["indexed"])
                for j in res:
                    if "AssetRetired" in j:
                        redeemed_bnusd = (i["data"][-1])
                        redeemed_bnusd = redeemed_bnusd.split(',')
                        for x in redeemed_bnusd:
                            x = x.replace(' ', '')
                            x = x.replace('}', '')
                            x = x.replace('{', '')
                            y = x.split(':')
                            sum += int(y[-1])
                        self.assertEqual((int(res[-1], 16)), sum, "The reduced value is not equal to the bnUSD burnt")

            # account positions after rebalancing
            after = {}
            for key, value in wallet_dict.items():
                after[key] = self.get_account_position(value)

            # users bnUSD retired percent
            before_list = list(before.keys())
            after_list = list(after.keys())
            change = []
            for i in range(len(wallet_dict)):
                if before[before_list[i]] != 0:
                    change.append((before[before_list[i]] - after[after_list[i]]) / before[before_list[i]] * 100)

            for i in range(len(change) - 1):
                self.assertEqual(change[i], change[i + 1], "Error in user retired bnUSD percent ")
            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self._test1.get_address()})
            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self.user1.get_address()})
            # self.call_tx(self.contracts['loans'], 'getAccountPositions', {"_owner": self.user2.get_address()})

            res = self.call_tx(self.contracts['bnUSD'], 'balanceOf', {"_owner": self.contracts['rebalancing']})
            self.assertEqual(int(res, 0), case['actions']['final_bnUSD_in_rebalancer'])

            self.call_tx(self.contracts['rebalancing'], 'getRebalancingStatus', {})

    def get_account_position(self, user: str) -> int:
        user_position = self.call_tx(self.contracts['loans'], 'getAccountPositions',
                                     {"_owner": user})
        if 'bnUSD' in user_position['assets']:
            return int(user_position['assets']['bnUSD'], 0)
        else:
            return 0