from iconservice import Address
from iconservice.base.exception import IconScoreException
from unittest import mock
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from core_contracts.rewards.rewards import Rewards

class MockClass:
    def __init__(self):
        class MockBaln:
            def mint(self, amount: int):
                pass

            def transfer(self, _to: Address, _value: int, _data: bytes = None):
                pass

        self.mockbaln = MockBaln()
        pass

    def create_interface_score(self, address: Address, score):
        return self.mockbaln

class TestRewards(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.mock_score = Address.from_string(f"cx{'1234'*10}")
        self.rewards = self.get_score_instance(Rewards, self.test_account1,
                                                 on_install_params={"_governance": self.mock_score})
        self.test_account3 = Address.from_string(f"hx{'12345' * 8}")
        self.test_account4 = Address.from_string(f"hx{'1234' * 10}")
        account_info = {
            self.test_account3: 10 ** 21,
            self.test_account4: 10 ** 21}
        self.initialize_accounts(account_info)

    def test_distribute(self):
        mock_class = MockClass()
        test_list = [{'recipient_name': 'Reserve Fund', 'dist_percent': 70 * 10 ** 16},
                      {'recipient_name': 'DAOfund', 'dist_percent': 10 * 10 ** 16},
                      {'recipient_name': 'Worker Tokens', 'dist_percent': 20 * 10 ** 16}]
        self.set_block(1, 1 * 24 * 60 * 60 * 10 ** 6)
        self.assertEqual(self.rewards.getRecipientsSplit(), {'Worker Tokens': 0, 'Reserve Fund': 0, 'DAOfund': 0})
        recipients_list = self.rewards.getRecipients()
        recipient_split = {}
        recipient_split_at_60 = {}
        for recipient in recipients_list:
            recipient_split[recipient] = self.rewards.recipientAt(recipient, 0)
            recipient_split_at_60[recipient] = self.rewards.recipientAt(recipient, 60)
        self.assertEqual(recipient_split, {'Worker Tokens': 0, 'Reserve Fund': 0, 'DAOfund': 0})
        self.assertEqual(recipient_split_at_60, {'Worker Tokens': 0, 'Reserve Fund': 0, 'DAOfund': 0})
        self.set_msg(self.mock_score)
        self.rewards.updateBalTokenDistPercentage(test_list)
        check_split = {}
        for x in test_list:
            name = x['recipient_name']
            per = x['dist_percent']
            check_split[name] = per
        self.assertEqual(self.rewards.getRecipientsSplit(), check_split)
        recipients_list = self.rewards.getRecipients()
        recipient_split = {}
        recipient_split_at_60 = {}
        recipient_split_at_1 = {}
        for recipient in recipients_list:
            recipient_split[recipient] = self.rewards.recipientAt(recipient, 0)
            recipient_split_at_60[recipient] = self.rewards.recipientAt(recipient, 60)
            recipient_split_at_1[recipient] = self.rewards.recipientAt(recipient, 1)
        self.assertEqual(recipient_split, {'Worker Tokens': 0, 'Reserve Fund': 0, 'DAOfund': 0})
        self.assertEqual(recipient_split_at_60, check_split)
        self.assertEqual(recipient_split_at_1, check_split)
        # print(self.rewards.recipientAt("Worker Tokens", 9))
        with mock.patch.object(self.rewards, "create_interface_score", wraps = mock_class.create_interface_score):
            self.set_block(1, 9 * 24 * 60 * 60 * 10**6)
            recipient_list = [{'recipient_name': 'Loans', 'dist_percent': 25 * 10 ** 16},
                      {'recipient_name': 'sICX/ICX', 'dist_percent': 10 * 10 ** 16},
                      {'recipient_name': 'Worker Tokens', 'dist_percent': 20 * 10 ** 16},
                      {'recipient_name': 'Reserve Fund', 'dist_percent': 5 * 10 ** 16},
                      {'recipient_name': 'DAOfund', 'dist_percent': 225 * 10 ** 15},
                      {'recipient_name': 'sICX/bnUSD', 'dist_percent': 175 * 10 ** 15}]
            for i, items_dict in enumerate(recipient_list):
                add = f"cx{str(i)*40}"
                if items_dict["recipient_name"] != "Worker Tokens" or items_dict["recipient_name"] != "Reserve Fund" or items_dict["recipient_name"] != "DAOfund" :
                    self.rewards.addNewDataSource(items_dict["recipient_name"], Address.from_string(add))
            # print(self.rewards.getRecipientsSplit())
            # print(self.rewards.recipientAt("Worker Tokens", 9))
            self.rewards.updateBalTokenDistPercentage(recipient_list)
            recipients_list = self.rewards.getRecipients()
            check_split2 ={}
            for x in recipient_list:
                name = x['recipient_name']
                per = x['dist_percent']
                check_split2[name] = per
            recipient_split = {}
            recipient_split_at_60 = {}
            recipient_split_at_1 = {}
            for recipient in recipients_list:
                recipient_split[recipient] = self.rewards.recipientAt(recipient, 0)
                recipient_split_at_60[recipient] = self.rewards.recipientAt(recipient, 60)
                recipient_split_at_1[recipient] = self.rewards.recipientAt(recipient, 1)
            self.assertEqual(recipient_split, {'Worker Tokens': 0, 'Reserve Fund': 0, 'DAOfund': 0, 'Loans': 0, 'sICX/ICX': 0, 'sICX/bnUSD': 0})
            self.assertEqual(recipient_split_at_60, check_split2)
            check_split["Loans"] = 0
            check_split["sICX/ICX"] = 0
            check_split["sICX/bnUSD"] = 0
            self.assertEqual(recipient_split_at_1, check_split)
            self.rewards.distribute()
            self.set_block(1, 11 * 24 * 60 * 60 * 10**6)
            self.rewards.distribute()

