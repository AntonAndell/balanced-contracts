from iconservice import *
from .utils.checks import *
from .scorelib import *

TAG = 'Dividends'

UNITS_PER_TOKEN = 1000000000000000000

# An interface of token to get balances.
class TokenInterface(InterfaceScore):
    @interface
    def balanceOf(self, _owner: Address) -> int:
        pass


# An interface tp the Loans SCORE to get the collateral token addresses.
class LoansInterface(InterfaceScore):
    @interface
    def getCollateralTokens(self) -> dict:
        pass

    @interface
    def getAssetTokens(self) -> dict:
        pass


class Dividends(IconScoreBase):

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog(indexed=2)
    def FundTransfer(self, destination: Address, amount: int, note: str):
        pass

    @eventlog(indexed=2)
    def TokenTransfer(self, recipient: Address, amount: int, note: str):
        pass

    _GOVERNANCE = 'governance'
    _ADMIN = 'admin'
    _LOANS_SCORE = 'loans_score'
    _DAOFUND = 'daofund'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._governance = VarDB(self._GOVERNANCE, db, value_type=Address)
        self._admin = VarDB(self._ADMIN, db, value_type=Address)
        self._loans_score = VarDB(self._LOANS_SCORE, db, value_type=Address)
        self._daofund = VarDB(self._DAOFUND, db, value_type=Address)

    def on_install(self, _governance: Address) -> None:
        super().on_install()
        self._governance.set(_governance)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return "Dividends"

    @external
    @only_owner
    def setGovernance(self, _address: Address) -> None:
        self._governance.set(_address)

    @external(readonly=True)
    def getGovernance(self) -> Address:
        return self._governance.get()

    @external
    @only_governance
    def setAdmin(self, _address: Address) -> None:
        self._admin.set(_address)

    @external(readonly=True)
    def getAdmin(self) -> Address:
        return self._admin.get()

    @external
    @only_admin
    def setLoans(self, _address: Address) -> None:
        self._loans_score.set(_address)

    @external(readonly=True)
    def getLoans(self) -> Address:
        return self._loans_score.get()

    @external
    @only_admin
    def setDaofund(self, _address: Address) -> None:
        self._daofund.set(_address)

    @external(readonly=True)
    def getDaofund(self) -> Address:
        return self._daofund.get()

    @external(readonly=True)
    def getBalances(self) -> dict:
        loans = self.create_interface_score(self._loans_score.get(), LoansInterface)
        assets = loans.getAssetTokens()
        balances = {}
        for symbol in assets:
            token = self.create_interface_score(Address.from_string(assets[symbol]), TokenInterface)
            balance = token.balanceOf(self.address)
            if balance > 0:
                balances[symbol] = balance
        balance = self.icx.get_balance(self.address)
        balances['ICX'] = balance
        return balances

    @external
    def distribute(self) -> bool:
        """
        A placeholder until BalancedDAO community decides how to handle fee revenue.
        """
        return True

    @external
    def claim(self) -> None:
        """
        A placeholder until BalancedDAO community decides how to handle fee revenue.
        """
        return True

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        """
        Used only to receive all fees generated by the Balanced system.
        :param _from: Token orgination address.
        :type _from: :class:`iconservice.base.address.Address`
        :param _value: Number of tokens sent.
        :type _value: int
        :param _data: Unused, ignored.
        :type _data: bytes
        """
        pass

    def _send_ICX(self, _to: Address, amount: int, msg: str) -> None:
        """
        Sends ICX to an address.
        :param _to: ICX destination address.
        :type _to: :class:`iconservice.base.address.Address`
        :param _amount: Number of ICX sent.
        :type _amount: int
        :param msg: Message for the event log.
        :type msg: str
        """
        try:
            self.icx.transfer(_to, amount)
            self.FundTransfer(_to, amount, msg + f' {amount} ICX sent to {_to}.')
        except BaseException as e:
            revert(f'{amount} ICX not sent to {_to}. '
                   f'Exception: {e}')

    @payable
    def fallback(self):
        pass
