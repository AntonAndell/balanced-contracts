import time

from ..test_integrate_base_loans import BalancedTestBaseLoans
from ..stories.loans.deposit_borrow_stories import DEPOSIT_AND_BORROW_STORIES


class BalancedTestDepositAndBorrow(BalancedTestBaseLoans):

    def setUp(self):
        super().setUp()

    def test_addCollateral(self):
        # sending ICX to the wallet
        self.send_icx(self.btest_wallet, self.user1.get_address(), 2500 * 10 ** 18)
        self.send_icx(self.btest_wallet, self.user2.get_address(), 2500 * 10 ** 18)

        test_cases = DEPOSIT_AND_BORROW_STORIES
        for case in test_cases['stories']:
            _tx_result = {}
            print(case['description'])
            if case['actions']['sender'] == 'user1':
                wallet_address = self.user1.get_address()
                wallet = self.user1
            else:
                wallet_address = self.user2.get_address()
                wallet = self.user2
            data1 = case['actions']['args']
            params = {"_asset": data1['_asset'], "_amount": data1['_amount']}

            # building transaction
            signed_transaction = self.build_tx(wallet, self.contracts['loans'], case['actions']['deposited_icx'],
                                               "depositAndBorrow", params)
            # process transaction
            _tx_result = self.process_transaction(signed_transaction, self.icon_service)

            if 'revertMessage' in case['actions'].keys():
                self.assertEqual(_tx_result['failure']['message'], case['actions']['revertMessage'])
            else:
                bal_of_sicx = self.balanceOfTokens('sicx', self.contracts['loans'])
                bal_of_bnUSD = self.balanceOfTokens('bnUSD', self.user1.get_address())

                # checks the status of tx
                self.assertEqual(1, _tx_result['status'])

                # checks the minted sicx and bnusd amount
                self.assertEqual(case['actions']['expected_sicx_baln_loan'], int(bal_of_sicx, 16))
                self.assertEqual(case['actions']['expected_bnUSD_debt_baln_loan'], int(bal_of_bnUSD, 16))

                account_position = self._getAccountPositions(self.user1.get_address())
                assets = account_position['assets']
                fee = self.balanceOfTokens('bnUSD', self.contracts['feehandler'])
                position_to_check = {'sICX': str(bal_of_sicx),
                                     'bnUSD': hex(int(bal_of_bnUSD, 16) + int(fee, 16))}
                self.assertEqual(position_to_check, assets)

        # update loans and rewards and governance and dex
        self.update('loans')
        self.update('rewards')
        self.update('governance')
        # self.update('dex')

        day = (self.call_tx(self.contracts["loans"], "getDay"))
        # day changes each 2 minutes.
        # set continuous rewards day as next day of current day.
        self.send_tx(self.btest_wallet, self.contracts['governance'], 0, "setContinuousRewardsDay", {"_day": int(day, 16) +1})

        continuous_day = (self.call_tx(self.contracts["loans"], "getContinuousRewardsDay"))
        print("Waiting for day change")
        # code pauses for 60 sec
        time.sleep(60)
        # testing for continuous rewards starts from here
        current_day = int(self.call_tx(self.contracts["loans"], "getDay"), 16)
        # asserting the continuous rewards day
        self.assertEqual(int(continuous_day, 16), current_day)

    def balanceOfTokens(self, name, address):
        params = {
            "_owner": address
        }
        response = self.call_tx(self.contracts[name], "balanceOf", params)
        return response

    def _getAccountPositions(self, address) -> dict:
        params = {'_owner': address}
        result = self.call_tx(self.contracts['loans'], "getAccountPositions", params)
        return result
