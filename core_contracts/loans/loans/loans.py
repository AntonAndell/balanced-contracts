# Copyright 2021 Balanced DAO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from iconservice import *
from ..utils.checks import *
from ..utils.consts import *
from .positions import PositionsDB
from .assets import AssetsDB, Asset


class PrepDelegations(TypedDict):
    _address: Address
    _votes_in_per: int


# An interface to the Emergency Reserve Fund
# TODO: Do we support other collaterals in reserve?
class ReserveFund(InterfaceScore):
    @interface
    def redeem(self, _to: Address, _amount: int, _sicx_rate: int) -> int:
        pass


# An interface to the Staking Management SCORE
class Staking(InterfaceScore):
    @interface
    def stakeICX(self, _to: Address = None, _data: bytes = None) -> int:
        pass

    @interface
    def delegate(self, _user_delegations: List[PrepDelegations]):
        pass


# An interface to the Rewards SCORE
class Rewards(InterfaceScore):
    @interface
    def distribute(self) -> bool:
        pass


# An interface to the Dividends SCORE
class Dividends(InterfaceScore):
    @interface
    def distribute(self) -> bool:
        pass


# An interface of token
class TokenInterface(InterfaceScore):
    @interface
    def symbol(self) -> str:
        pass

    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        pass


# TODO: Need new universale method to trade tokens
class DexTokenInterface(InterfaceScore):
    @interface
    def getSicxBnusdPrice(self) -> int:
        pass


class Loans(IconScoreBase):
    _LOANS_ON = 'loans_on'
    _GOVERNANCE = 'governance'
    _REBALANCE = 'rebalance'
    _DEX = 'dex'
    _DIVIDENDS = 'dividends'
    _RESERVE = 'reserve'
    _REWARDS = 'rewards'
    _STAKING = 'staking'
    _ADMIN = 'admin'
    _SNAP_BATCH_SIZE = 'snap_batch_size'
    _GLOBAL_INDEX = 'global_index'
    _GLOBAL_BATCH_INDEX = 'global_batch_index'

    _REWARDS_DONE = 'rewards_done'
    _DIVIDENDS_DONE = 'dividends_done'
    _CURRENT_DAY = 'current_day'
    _TIME_OFFSET = 'time_offset'

    _MINING_RATIO = 'mining_ratio'
    _LOCKING_RATIO = 'locking_ratio'
    _LIQUIDATION_RATIO = 'liquidation_ratio'
    _ORIGINATION_FEE = 'origination_fee'
    _REDEMPTION_FEE = 'redemption_fee'
    _RETIREMENT_BONUS = 'retirement_bonus'
    _LIQUIDATION_REWARD = 'liquidation_reward'
    _NEW_LOAN_MINIMUM = 'new_loan_minimum'
    _MIN_MINING_DEBT = 'min_mining_debt'
    _MAX_DEBTS_LIST_LENGTH = 'max_debts_list_length'

    _REDEEM_BATCH_SIZE = 'redeem_batch_size'
    _MAX_RETIRE_PERCENT = 'max_retire_percent'
    _COLLATERAL_EXPECTED = 'collateral_expected'
    _COLLATERAL_RECEIVED = 'collateral_received'
    _DEBT_TOKEN_EXPECTED = 'debt_token_expected'
    _DEBT_TOKEN_RECEIVED = 'debt_token_received'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._loans_on = VarDB(self._LOANS_ON, db, value_type=bool)
        self._governance = VarDB(self._GOVERNANCE, db, value_type=Address)
        self._rebalance = VarDB(self._REBALANCE, db, value_type=Address)
        self._dex = VarDB(self._DEX, db, value_type=Address)
        self._dividends = VarDB(self._DIVIDENDS, db, value_type=Address)
        self._reserve = VarDB(self._RESERVE, db, value_type=Address)
        self._rewards = VarDB(self._REWARDS, db, value_type=Address)
        self._staking = VarDB(self._STAKING, db, value_type=Address)
        self._admin = VarDB(self._ADMIN, db, value_type=Address)
        self._snap_batch_size = VarDB(self._SNAP_BATCH_SIZE, db, value_type=int)
        self._global_index = VarDB(self._GLOBAL_INDEX, db, value_type=int)
        self._global_batch_index = VarDB(self._GLOBAL_BATCH_INDEX, db, value_type=int)

        self._assets = AssetsDB(db, self)
        self._positions = PositionsDB(db, self)
        self._rewards_done = VarDB(self._REWARDS_DONE, db, value_type=bool)
        self._dividends_done = VarDB(self._DIVIDENDS_DONE, db, value_type=bool)
        self._current_day = VarDB(self._CURRENT_DAY, db, value_type=int)
        self._time_offset = VarDB(self._TIME_OFFSET, db, value_type=int)

        self._mining_ratio = VarDB(self._MINING_RATIO, db, value_type=int)
        self._locking_ratio = VarDB(self._LOCKING_RATIO, db, value_type=int)
        self._liquidation_ratio = VarDB(self._LIQUIDATION_RATIO, db, value_type=int)
        self._origination_fee = VarDB(self._ORIGINATION_FEE, db, value_type=int)
        self._redemption_fee = VarDB(self._REDEMPTION_FEE, db, value_type=int)
        self._retirement_bonus = VarDB(self._RETIREMENT_BONUS, db, value_type=int)
        self._liquidation_reward = VarDB(self._LIQUIDATION_REWARD, db, value_type=int)
        self._new_loan_minimum = VarDB(self._NEW_LOAN_MINIMUM, db, value_type=int)
        self._min_mining_debt = VarDB(self._MIN_MINING_DEBT, db, value_type=int)
        self._max_debts_list_length = VarDB(self._MAX_DEBTS_LIST_LENGTH, db, value_type=int)

        # batch size for redeem-retire
        self._redeem_batch = VarDB(self._REDEEM_BATCH_SIZE, db, value_type=int)
        # max percentage of the batch total debt that can be accepted in one redemption.
        self._max_retire_percent = VarDB(self._MAX_RETIRE_PERCENT, db, value_type=int)
        self._collateral_expected = VarDB(self._COLLATERAL_EXPECTED, db, value_type=bool)
        self._collateral_received = VarDB(self._COLLATERAL_RECEIVED, db, value_type=int)
        self._debt_token_expected = VarDB(self._DEBT_TOKEN_EXPECTED, db, value_type=bool)
        self._debt_token_received = VarDB(self._DEBT_TOKEN_RECEIVED, db, value_type=int)

        self.migration_flags = DictDB("migration_flag", db, value_type=bool)

    def on_install(self, _governance: Address) -> None:
        super().on_install()
        self._governance.set(_governance)
        self._loans_on.set(False)
        self._admin.set(self.owner)
        self._snap_batch_size.set(SNAP_BATCH_SIZE)
        self._rewards_done.set(True)
        self._dividends_done.set(True)
        self._mining_ratio.set(MINING_RATIO)
        self._locking_ratio.set(LOCKING_RATIO)
        self._liquidation_ratio.set(LIQUIDATION_RATIO)
        self._origination_fee.set(ORIGINATION_FEE)
        self._redemption_fee.set(REDEMPTION_FEE)
        self._liquidation_reward.set(LIQUIDATION_REWARD)
        self._retirement_bonus.set(BAD_DEBT_RETIREMENT_BONUS)
        self._new_loan_minimum.set(NEW_LOAN_MINIMUM)
        self._min_mining_debt.set(MIN_MINING_DEBT)
        self._redeem_batch.set(REDEEM_BATCH_SIZE)
        self._max_retire_percent.set(MAX_RETIRE_PERCENT)
        self._max_debts_list_length.set(MAX_DEBTS_LIST_LENGTH)

    def on_update(self) -> None:
        super().on_update()

    # BEGIN: TEMPORARY METHODS TO BE REMOVED AFTER MIGRATION #
    # TODO: REMOVE THE METHODS BELOW AFTER MIGRATION IS COMPLETE
    @external
    def migrate_user(self, _address: Address) -> None:
        if self.msg.sender not in [self.owner, _address]:
            revert("Only score owner or wallet can perform this task.")
        pos = self._positions.get_pos(_address)
        for symbol in pos.asset_db.symbol_list:
            value = pos.assets[pos.snaps[-1]][symbol]
            if symbol == 'sicx':
                pos.collateral_owned["sicx"] = value
            else:
                pos.set_loan_amt("sicx", symbol, value)

    @external
    def migrate_market(self, asset_symbol: str):
        if self.msg.sender != self.owner:
            revert("Only score owner or wallet can perform this task.")
        if self.migration_flags[asset_symbol]:
            revert(f"{asset_symbol} has already been migrated.")
        if asset_symbol not in self._assets.active_address_list:
            revert("Asset symbol must be a active address list.")

        asset = self._assets[asset_symbol]

        dead_market = asset.old_dead_market.get()
        bad_debt = asset.old_bad_debt.get()
        liquidation_pool = asset.old_liquidation_pool.get()

        asset.dead_market["sicx"] = dead_market
        asset.bad_debt["sicx"] = bad_debt
        asset.liquidation_pool["sicx"] = liquidation_pool

        self.migration_flags[asset_symbol] = True

    # END: TEMPORARY METHODS TO BE REMOVED AFTER MIGRATION #

    @external
    @only_owner
    def setNextNode(self, _node_id: int) -> None:
        self._positions.next_node.set(_node_id)

    @external(readonly=True)
    def getNextNode(self) -> int:
        return self._positions.next_node.get()

    @external(readonly=True)
    def getMetaData(self) -> str:
        nonzero = self._positions.get_nonzero()
        return nonzero.get_metadata()

    @external(readonly=True)
    def name(self) -> str:
        return "Balanced Loans"

    @external
    @only_governance
    def turnLoansOn(self) -> None:
        self._loans_on.set(True)
        self.ContractActive("Loans", "Active")
        self._current_day.set(self.getDay())
        self._positions._snapshot_db.start_new_snapshot()

    @external
    @only_governance
    def toggleLoansOn(self) -> None:
        value: bool = not self._loans_on.get()
        self._loans_on.set(value)
        self.ContractActive("Loans", "Active" if value else "Inactive")

    @external(readonly=True)
    def getLoansOn(self) -> bool:
        return self._loans_on.get()

    @external(readonly=True)
    def getDay(self) -> int:
        return (self.now() - self._time_offset.get()) // U_SECONDS_DAY

    @external
    @only_governance
    def delegate(self, _delegations: List[PrepDelegations]):
        """
        Sets the delegation preference for the sICX held on the contract.
        :param _delegations: List of dictionaries with two keys, Address and percent.
        :type _delegations: List[PrepDelegations]
        """
        staking = self.create_interface_score(self._staking.get(), Staking)
        staking.delegate(_delegations)

    @external(readonly=True)
    def getDistributionsDone(self) -> dict:
        return {"Rewards": self._rewards_done.get(),
                "Dividends": self._dividends_done.get()}

    @external(readonly=True)
    def getDebts(self, _address_list: List[str], _day: int) -> dict:
        """
        Returns the debt held by each address in the list.
        """
        max_length = self._max_debts_list_length.get()
        if len(_address_list) > max_length:
            revert(f'{TAG}: Address list is longer than the maximum '
                   f'allowable length ({max_length}).')
        debts = {}
        for address in _address_list:
            pos_id = self._positions.get_id_for(Address.from_string(address))
            snapshot = self._positions._snapshot_db[_day]
            debts[address] = snapshot.pos_state[pos_id]['total_debt']
        return debts

    @external(readonly=True)
    def checkDeadMarkets(self) -> list:
        """
        Returns the symbols for all assets with dead_market status.
        """
        return [
            symbol
            for symbol in self._assets.active_address_list
            if self._assets[symbol].dead_market.get()
        ]

    @external(readonly=True)
    def getNonzeroPositionCount(self) -> int:
        """
        Returns the total number of nonzero positions.
        """
        pos = self._positions
        snap = pos._snapshot_db[-1]
        nonzero = len(pos.get_nonzero()) + len(snap.get_add_nonzero()) - len(snap.get_remove_nonzero())
        if snap.snap_day.get() > 1:
            last_snap = pos._snapshot_db[-2]
            nonzero += len(last_snap.get_add_nonzero()) - len(last_snap.get_remove_nonzero())
        return nonzero

    @external(readonly=True)
    def getPositionStanding(self, _address: Address) -> dict:
        """
        Returns the current standing for a position.
        """
        pos = self._positions.get_pos(_address)
        status = pos.get_standing(_readonly=True)
        status['standing'] = Standing.STANDINGS[status['standing']]
        return status

    @external(readonly=True)
    def getPositionAddress(self, _index: int) -> Address:
        """
        returns the address of a position given its index. Enables iteration over
        all positions in Balanced.
        """
        return self._positions[_index].address.get()

    @external(readonly=True)
    def getAssetTokens(self) -> dict:
        """
        Returns a dictionary of assets from the assetsDB with token symbol as
        the key and address as a string value.
        """
        return {
            symbol: self._assets.symbol_dict[symbol] for symbol in self._assets.symbol_list
        }

    @external(readonly=True)
    def getCollateralTokens(self) -> dict:
        """
        Returns a dictionary of assets from the assetsDB that are marked as
        collateral, with token symbol as the key and address as a string value.
        """
        return {
            symbol: self._assets.symbol_dict[symbol]
            for symbol in self._assets.symbol_list
            if self._assets[symbol].is_collateral()
        }

    @external(readonly=True)
    def getTotalCollateral(self) -> int:
        """
        Sum of all active collateral held on the loans SCORE in loop.
        Read-only; does not check for a more recent price update.
        """
        total_collateral = 0
        for symbol in self._assets.symbol_list:
            asset = self._assets[symbol]
            if asset.is_collateral() and asset.is_active():
                held = asset.balanceOf(self.address)
                price = asset.lastPriceInLoop()
                total_collateral += held * price
        return total_collateral // EXA

    @external(readonly=True)
    def getAccountPositions(self, _owner: Address) -> dict:
        """
        Get account positions.
        """
        return self._positions.list_pos(_owner)

    @external(readonly=True)
    def getPositionByIndex(self, _index: int) -> dict:
        """
        Get account positions.
        """
        return self._positions[_index].to_dict()

    @external(readonly=True)
    def getAvailableAssets(self) -> dict:
        """
        Returns a dict of assets.
        """
        return self._assets.get_assets()

    @external(readonly=True)
    def assetCount(self) -> int:
        """
        Returns the number of assets in the AssetsDB.
        """
        return len(self._assets)

    @external(readonly=True)
    def borrowerCount(self) -> int:
        """
        Returns the number of borrowers on Balanced.
        """
        return len(self._positions)

    @external(readonly=True)
    def hasDebt(self, _owner: Address, collateral: str = '', symbol: str = '') -> bool:
        """
        Returns whether the address holds a debt position.
        """
        pos = self._positions.get_pos(_owner)
        return pos.has_debt(collateral, symbol)

    @external(readonly=True)
    def getSnapshot(self, _snap_id: int = -1) -> dict:
        """
        Returns a summary of the snapshot for the system. Returns an empty dict
        for snapshot indexes that are out of range.
        """
        if (_snap_id > self._positions._snapshot_db._indexes[-1] or
                _snap_id + len(self._positions._snapshot_db._indexes) < 0):
            return {}
        return self._positions._snapshot_db[_snap_id].to_dict()

    @external
    @only_admin
    def addAsset(self, _token_address: Address,
                 _active: bool = True,
                 _collateral: bool = False) -> None:
        """
        Adds a token to the assets dictionary.
        """
        self._assets.add_asset(_token_address, _active, _collateral)
        token_score = self.create_interface_score(_token_address, TokenInterface)
        self.AssetAdded(_token_address, token_score.symbol(), _collateral)

    @external
    @only_admin
    def toggleAssetActive(self, _symbol: str) -> None:
        asset = self._assets[_symbol]
        value: bool = not asset.is_active()
        asset._active.set(value)
        self.AssetActive(_symbol, "Active" if value else "Inactive")

    @external
    def precompute(self, _snapshot_id: int, batch_size: int) -> bool:
        """
        prepares the position data snapshot to send to the rewards SCORE.
        """
        if self.msg.sender != self._rewards.get():
            revert(f'{TAG}: The precompute method may only be invoked by the rewards SCORE.')
        self.checkForNewDay()  # Only does something if it is internal on a DEX tx.
        # Iterate through all positions in the snapshot to bring them up to date.
        if self._positions._calculate_snapshot(_snapshot_id, batch_size):
            return Complete.DONE
        return Complete.NOT_DONE

    @external(readonly=True)
    def getTotalValue(self, _name: str, _snapshot_id: int) -> int:
        """
        Gets total outstanding debt for mining rewards calculation.
        """
        return self._positions._snapshot_db[_snapshot_id].total_mining_debt.get()

    @external(readonly=True)
    def getBnusdValue(self, _name: str) -> int:
        """
        Returns the total bnUSD value of loans mining BALN for APY calculation.
        """
        bnUSD_price = self._positions._snapshot_db[-2].prices['bnUSD']
        loop_value = self._positions._snapshot_db[-2].total_mining_debt.get()
        return EXA * loop_value // bnUSD_price

    @external(readonly=True)
    def getDataCount(self, _snapshot_id: int) -> int:
        """
        Returns the number of records in the snapshot.
        """
        return len(self._positions._snapshot_db[_snapshot_id].mining)

    @external(readonly=True)
    def getDataBatch(self, _name: str, _snapshot_id: int,
                     _limit: int, _offset: int = 0) -> dict:
        """
        Read position data batch.
        """
        batch = {}
        snapshot = self._positions._snapshot_db[_snapshot_id]
        total_mining = len(snapshot.mining)
        start = max(0, min(_offset, total_mining))
        end = min(_offset + _limit, total_mining)
        for i in range(start, end):
            pos_id = snapshot.mining[i]
            pos = self._positions[pos_id]
            batch[str(pos.address.get())] = snapshot.pos_state[pos_id]['total_debt']
        return batch

    @loans_on
    @external
    def checkForNewDay(self) -> (int, bool):
        day = self.getDay()
        new_day: bool = False
        if day > self._current_day.get():
            new_day = True
            self._current_day.set(day)
            self._positions._take_snapshot()
            self.check_dead_markets()
        return day, new_day

    @loans_on
    @external
    def checkDistributions(self, _day: int, _new_day: bool) -> None:
        rewards_done: bool = self._rewards_done.get()
        dividends_done: bool = self._dividends_done.get()

        if _new_day and rewards_done and dividends_done:
            self._rewards_done.set(False)
            self._dividends_done.set(False)
        elif not dividends_done:
            dividends = self.create_interface_score(self._dividends.get(), Dividends)
            self._dividends_done.set(dividends.distribute())
        elif not rewards_done:
            rewards = self.create_interface_score(self._rewards.get(), Rewards)
            self._rewards_done.set(rewards.distribute())

    @loans_on
    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        """
        Directs incoming tokens to deposit collateral or return an asset.
        :param _from: Address of the token sender.
        :type _from: :class:`iconservice.base.address.Address`
        :param _value: Number of tokens sent.
        :type _value: int
        :param _data: Method and parameters to call once tokens are received.
        :type _data: bytes
        """
        if _value <= 0:
            revert(f'{TAG}: Amount sent must be greater than zero.')
        addresses = {address: idx for idx, address in enumerate(self._assets.address_list)}
        if self.msg.sender not in addresses:
            revert(f'{TAG}: The Balanced Loans contract does not accept that token type.')
        debt_token_symbol = self._assets.symbol_list[addresses[self.msg.sender]]
        debt_token_asset = self._assets[debt_token_symbol]
        if not debt_token_asset.is_collateral():
            if self._debt_token_expected.get():
                self._debt_token_received.set(_value)
            return
        if self._collateral_expected.get():
            self._collateral_received.set(_value)
            return
        try:
            d = json_loads(_data.decode("utf-8"))
        except Exception:
            revert(f'{TAG}: Invalid data: {_data}, returning tokens.')
        else:
            if set(d.keys()) == {"_asset", "_amount", "loan_collateral"}:
                self.depositAndBorrow(d['_asset'], d['_amount'], _from, _value, d['loan_collateral'])
            else:
                revert(f'{TAG}: Invalid parameters.')

    @loans_on
    @payable
    @external
    def depositAndBorrow(self, _asset: str = '', _amount: int = 0,
                         _from: Address = None, _value: int = 0, collateral_symbol: str = '') -> None:
        """
        This method may be used to deposit collateral and / or
        originate a loan of one of the assets supported by Balanced.
        If the optional parameters of _asset and _amount are present a loan of
        _amount of _asset will be returned to the originating address if
        there is sufficient collateral present.
        :param collateral_symbol: Symbol of collateral to take loan against
        :param _from: Sender address if collateral is received.
        :type _from: :class:`iconservice.base.address.Address`
        :param _value: Amount of collateral received.
        :type _value: int
        :param _asset: Symbol of asset to borrow.
        :type _asset: str
        :param _amount: Size of loan requested.
        :type _amount: int
        """
        deposit = self.msg.value
        sender = self.msg.sender

        # TODO: add logic for depositing new collaterals here
        if sender != self._assets['sICX'].get_address():
            _from = sender
            if deposit > 0:
                self._collateral_expected.set(True)
                staking = self.create_interface_score(self._staking.get(), Staking)
                staking.icx(deposit).stakeICX(self.address)
                received = self._collateral_received.get()
                if received == 0:
                    revert(f'{TAG}: Expected sICX not received.')
                _value = received
                self._collateral_received.set(0)
                self._collateral_expected.set(False)
            else:
                _value = 0
        day, new_day = self.checkForNewDay()
        self.checkDistributions(day, new_day)
        pos = self._positions.get_pos(_from)
        if _value > 0:
            new_collateral_value = pos.collateral_value(collateral_symbol) + _value
            pos.set_collateral_amt(collateral_symbol, new_collateral_value)
            self.CollateralReceived(_from, collateral_symbol, _value)
        if _asset == '' or _amount < 1 or collateral_symbol == '':
            return
        self._originate_loan(_asset, _amount, _from, collateral_symbol)

    @loans_on
    @external
    def retireBadDebt(self, collateral_symbol: str, _symbol: str, _value: int) -> None:
        """
         Returned assets come back to Balanced through this method.
         This will pay off bad debt in exchange for
        collateral from the liquidation pool.
        :param _symbol: retired token symbol.
        :type _symbol: str
        :param _value: Number of tokens sent.
        :type _value: int
        """
        _from = self.msg.sender
        if not _value > 0:
            revert(f'{TAG}: Amount retired must be greater than zero.')
        asset = self._assets[_symbol]
        if not (asset and asset.is_active()) or asset.is_collateral():
            revert(f'{TAG}: {_symbol} is not an active, borrowable asset on Balanced.')
        if asset.balanceOf(_from) < _value:
            revert(f'{TAG}: Insufficient balance.')
        bad_debt = asset.bad_debt[collateral_symbol]
        if bad_debt > 0:
            day, new_day = self.checkForNewDay()
            self.checkDistributions(day, new_day)
            bd_value = min(bad_debt, _value)
            asset.burnFrom(_from, bd_value)
            collateral = self.bd_redeem(collateral_symbol, _from, asset, bd_value)
            self._send_token(collateral_symbol, _from, collateral, "Bad Debt redeemed.")
            asset.is_dead(collateral_symbol)
            self.BadDebtRetired(_from, _symbol, bd_value, collateral)
        else:
            revert(f'{TAG}: No bad debt for {_symbol}.')

    @loans_on
    @external
    def returnAsset(self, collateral_symbol: str, _symbol: str, _value: int, _repay: bool = True) -> None:
        """
        A borrower will use this method to pay off their loan.
        :param _symbol: retired token symbol.
        :type _symbol: str
        :param _value: Number of tokens sent.
        :type _value: int
        :param _repay: Whether returned funds should be used to repay loan first.
        :type _repay: bool
        """
        _from = self.msg.sender
        if not _value > 0:
            revert(f'{TAG}: Amount retired must be greater than zero.')
        asset = self._assets[_symbol]
        if not (asset and asset.is_active()) or asset.is_collateral():
            revert(f'{TAG}: {_symbol} is not an active, borrowable asset on Balanced.')
        if asset.balanceOf(_from) < _value:
            revert(f'{TAG}: Insufficient balance.')
        if self._positions._exists(_from) and _repay:
            day, new_day = self.checkForNewDay()
            self.checkDistributions(day, new_day)
            pos = self._positions.get_pos(_from)
            if _value > pos.get_loans(collateral_symbol, _symbol):
                revert(f'{TAG}: Repaid amount is greater than the amount in the position of {_from}')
            if _value > 0:
                borrowed = pos.get_loans(collateral_symbol, _symbol)
                remaining = borrowed - _value
                if remaining > 0:
                    pos.set_loan_amt(collateral_symbol, _symbol, remaining)
                    repaid = _value
                else:
                    repaid = borrowed
                    pos.clear_loans(collateral_symbol, _symbol)
                    pos_id = pos.id.get()
                    if not pos.has_debt():
                        self._positions.remove_nonzero(pos_id)
                asset.burnFrom(_from, repaid)
                self.LoanRepaid(_from, _symbol, repaid,
                                f'Loan of {repaid} {_symbol} repaid to Balanced.')
                asset.is_dead(collateral_symbol)
            return
        else:
            revert(f'{TAG}: No debt repaid because,'
                   f'{_from} does not have a position in Balanced' if _repay else f'{_repay == False}')

    @loans_on
    @external
    @only_rebalance
    def raisePrice(self, collateral_symbol: str, _symbol: str, _total_tokens_required: int) -> None:
        """
        This function will  pay off debt from a batch of
        borrowers proportionately, selling a share of collateral from each
        position in the batch.
        :param _total_tokens_required: Maximum tokens amount required to balance the pool.
        :type _total_tokens_required: int
        """
        asset = self._assets[_symbol]

        dex_score = self.create_interface_score(self._dex.get(), DexTokenInterface)
        # todo: create universal method
        rate = dex_score.getSicxBnusdPrice()

        batch_size = self._redeem_batch.get()
        borrowers = asset.get_borrowers(collateral_symbol)
        node_id = borrowers.get_head_id()
        total_batch_debt: int = 0
        positions_dict = {}
        for _ in range(min(batch_size, len(borrowers))):
            user_debt = borrowers.node_value(node_id)
            positions_dict[node_id] = user_debt
            total_batch_debt += user_debt
            borrowers.move_head_to_tail()
            node_id = borrowers.get_head_id()
        borrowers.serialize()

        collateral_to_sell = min(_total_tokens_required,
                                 (self._max_retire_percent.get() * total_batch_debt * EXA)
                                 // (POINTS * rate))

        swap_data = b'{"method":"_swap","params":{"toToken":"' + str(asset.get_address()).encode('utf-8') + b'"}}'

        self._debt_token_expected.set(True)
        self._send_token(collateral_symbol, self._dex.get(), collateral_to_sell,
                         f"{collateral_symbol} swapped for {_symbol}", swap_data)
        debt_token_received = self._debt_token_received.get()
        self._debt_token_received.set(0)
        self._debt_token_expected.set(False)
        asset.burnFrom(self.address, debt_token_received)

        remaining_supply = total_batch_debt
        remaining_debt_token = debt_token_received
        change_in_pos_dict = {}

        for pos_id, user_debt in positions_dict.items():
            loan_share = remaining_debt_token * user_debt // remaining_supply
            remaining_debt_token -= loan_share
            pos = self._positions[pos_id]
            pos.set_loan_amt(collateral_symbol, _symbol, user_debt - loan_share)

            collateral_share = collateral_to_sell * user_debt // remaining_supply
            collateral_to_sell -= collateral_share
            new_collateral_value = pos.collateral_value(collateral_symbol) - collateral_share
            pos.set_collateral_amt(collateral_symbol, new_collateral_value)

            remaining_supply -= user_debt
            change_in_pos_dict[pos_id] = {"d": -loan_share, "c": -collateral_share}

        self.Rebalance(self.msg.sender, _symbol, str(change_in_pos_dict),
                       total_batch_debt)

    @loans_on
    @external
    @only_rebalance
    def lowerPrice(self, collateral_symbol: str, symbol: str, _total_tokens_required: int) -> None:
        """
        This function will add debt to a batch of
        borrowers proportionately along with their collateral.
        :param _total_tokens_required: Maximum tokens amount required to balance the pool.
        :type _total_tokens_required: int
        """
        batch_size = self._redeem_batch.get()
        borrowers = self._assets[symbol].get_borrowers(collateral_symbol)
        node_id = borrowers.get_head_id()
        total_batch_debt: int = 0
        positions_dict = {}
        for _ in range(min(batch_size, len(borrowers))):
            user_debt = borrowers.node_value(node_id)
            positions_dict[node_id] = user_debt
            total_batch_debt += user_debt
            borrowers.move_head_to_tail()
            node_id = borrowers.get_head_id()
        borrowers.serialize()

        debt_token_to_sell = min(_total_tokens_required,
                                 (self._max_retire_percent.get() * total_batch_debt // POINTS))

        self._debt_token_expected.set(True)
        self._assets[symbol].mint(self.address, debt_token_to_sell)
        self._debt_token_received.set(0)
        self._debt_token_expected.set(False)

        swap_data = b'{"method":"_swap","params":{"toToken":"' + str(
            self._assets[collateral_symbol].get_address()).encode('utf-8') + b'"}}'

        self._collateral_expected.set(True)
        # TODO: SUYOG : direct market between collateral and symbol in dex
        self._send_token(symbol, self._dex.get(), debt_token_to_sell, f"{symbol} swapped for {collateral_symbol}",
                         swap_data)
        received_collateral = self._collateral_received.get()
        self._collateral_received.set(0)
        self._collateral_expected.set(False)

        remaining_collateral = received_collateral
        remaining_supply = total_batch_debt
        remaining_debt_token = debt_token_to_sell
        change_in_pos_dict = {}
        for pos_id, user_debt in positions_dict.items():
            loan_share = remaining_debt_token * user_debt // remaining_supply
            remaining_debt_token -= loan_share
            pos = self._positions[pos_id]
            pos.set_loan_amt(collateral_symbol, symbol, user_debt + loan_share)

            collateral_share = remaining_collateral * user_debt // remaining_supply
            remaining_collateral -= collateral_share
            pos.set_collateral_amt(collateral_symbol, pos.collateral_value(collateral_symbol) + collateral_share)

            remaining_supply -= user_debt
            change_in_pos_dict[str(pos_id)] = {"d": loan_share, "c": collateral_share}

        self.Rebalance(self.msg.sender, symbol, str(change_in_pos_dict),
                       total_batch_debt)

    def bd_redeem(self, collarteral_symbol: str, _from: Address,
                  _asset: Asset,
                  _bd_value: int) -> int:
        """
        Returns the amount of the bad debt paid off in collateral coming from both
        the liquidation pool for the asset or the ReserveFund SCORE.
        :param _from: Address of the token sender.
        :type _from: :class:`iconservice.base.address.Address`
        :param _asset: Balanced Asset that is being redeemed.
        :type _asset: :class:`loans.assets.Asset`
        :param _bd_value: Amount of bad debt to redeem.
        :type _bd_value: int
        :return: Amount of collateral supplied from reserve.
        :rtype: int
        """
        _price = _asset.priceInLoop()
        _collateral_rate = self._assets[collarteral_symbol].priceInLoop()
        reserve_address = self._reserve.get()
        in_pool = _asset.liquidation_pool.get()
        bad_debt = _asset.bad_debt.get() - _bd_value
        _asset.bad_debt.set(bad_debt)
        bd_collateral = ((POINTS + self._retirement_bonus.get())
                         * _bd_value * _price // (POINTS * _collateral_rate))
        if in_pool >= bd_collateral:
            _asset.liquidation_pool.set(in_pool - bd_collateral)
            if bad_debt == 0:
                self._send_token(collarteral_symbol, reserve_address,
                                 in_pool - bd_collateral, "Sweep to ReserveFund:")
                _asset.liquidation_pool.set(0)
            return bd_collateral
        _asset.liquidation_pool.set(0)
        reserve = self.create_interface_score(reserve_address, ReserveFund)
        self._collateral_expected.set(True)
        reserve.redeem(_from, bd_collateral - in_pool, _collateral_rate)
        if self._collateral_received.get() != (bd_collateral - in_pool):
            revert(f'Got unexpected {collarteral_symbol} from reserve.')
        received = self._collateral_received.get()
        self._collateral_received.set(0)
        self._collateral_expected.set(False)
        return in_pool + received

    def _originate_loan(self, _asset: str, _amount: int, _from: Address, collateral_symbol: str) -> None:
        """
        Originate a loan of an asset if there is sufficient collateral.
        :param _asset: Symbol of the asset.
        :type _asset: str
        :param _amount: Number of tokens sent.
        :type _amount: int
        :param _from
        :type _from: Address
        """
        asset = self._assets[_asset]
        if asset.is_dead(collateral_symbol):
            revert(f'{TAG}: No new loans of {_asset} can be originated since '
                   f'it is in a dead market state.')
        if asset.is_collateral():
            revert(f'{TAG}: Loans of collateral assets are not allowed.')
        if not asset.is_active():
            revert(f'{TAG}: Loans of inactive assets are not allowed.')
        pos = self._positions.get_pos(_from)

        # Check for sufficient collateral
        collateral = pos.collateral_value(symbol=collateral_symbol)
        max_debt_value = POINTS * collateral // self._locking_ratio.get()
        fee = self._origination_fee.get() * _amount // POINTS
        new_debt_value = self._assets[_asset].priceInLoop() * (_amount + fee) // EXA

        # Check for loan minimum
        pos_id = pos.id.get()
        if pos.get_loans(collateral_symbol, _asset) == 0:
            loan_minimum = self._new_loan_minimum.get()
            dollar_value = new_debt_value * EXA // self._assets[_asset].priceInLoop()
            if dollar_value < loan_minimum:
                revert(f'{TAG}: The initial loan of any asset must have a minimum value '
                       f'of {loan_minimum / EXA} dollars.')
        total_debt = pos.total_debt(collateral_symbol)
        if total_debt + new_debt_value > max_debt_value:
            revert(f'{TAG}: {collateral / EXA} collateral is insufficient'
                   f' to originate a loan of {_amount / EXA} {_asset}'
                   f' when max_debt_value = {max_debt_value / EXA},'
                   f' new_debt_value = {new_debt_value / EXA},'
                   f' which includes a fee of {fee / EXA} {_asset},'
                   f' given an existing loan value of {total_debt / EXA}.')

        # Originate loan
        if total_debt == 0:
            self._positions.add_nonzero(pos_id)
        new_debt = _amount + fee
        pos.set_loan_amt(collateral_symbol, _asset,
                         value=pos.get_loans(collateral_symbol, _asset) + new_debt)
        self.OriginateLoan(_from, _asset, _amount,
                           f'Loan of {_amount} {_asset} from Balanced.')
        self._assets[_asset].mint(_from, _amount)

        # Pay fee
        self._assets[_asset].mint(self._dividends.get(), fee)
        self.FeePaid(_asset, fee, "origination")

    @loans_on
    @external
    def withdrawCollateral(self, symbol: str, _value: int) -> None:
        """
        Withdraw collateral up to the collateral locking ratio.
        :param _value: Amount of collateral to withdraw.
        :type _value: int
        """
        if _value <= 0:
            revert(f'{TAG}: Withdraw amount must be more than zero.')
        _from = self.msg.sender
        if not self._positions._exists(_from):
            revert(f'{TAG}: This address does not have a position on Balanced.')
        day, new_day = self.checkForNewDay()
        self.checkDistributions(day, new_day)
        pos = self._positions.get_pos(_from)

        if pos.collateral_value(symbol) < _value:
            revert(f'{TAG}: Position holds less collateral than the requested withdrawal.')
        asset_value = pos.total_debt(collateral=symbol)  # Value in ICX
        remaining_collateral = pos.collateral_value(symbol) - _value
        remaining_coll = remaining_collateral * self._assets[symbol].priceInLoop() // EXA
        locking_value = self._locking_ratio.get() * asset_value // POINTS
        if remaining_coll < locking_value:
            revert(f'{TAG}: Requested withdrawal is more than available collateral. '
                   f'total debt value: {asset_value} ICX '
                   f'remaining collateral value: {remaining_coll} ICX '
                   f'locking value (max debt): {locking_value} ICX')
        pos.set_collateral_amt(symbol, remaining_collateral)
        self._send_token(symbol, _from, _value, "Collateral withdrawn.")

    @loans_on
    @external
    def liquidate(self, _owner: Address, collateral_symbol: str) -> None:
        """
        Liquidate collateral if the position is below the liquidation threshold.
        :param _owner: Address of position to update.
        :type _owner: :class:`iconservice.base.address.Address`
        """
        if not self._positions._exists(_owner):
            revert(f'{TAG}: This address does not have a position on Balanced.')
        pos = self._positions.get_pos(_owner)
        _standing = pos.get_standing(collateral_symbol)
        if _standing == Standing.LIQUIDATE:
            pos_id = pos.id.get()
            collateral = pos.collateral_value(collateral_symbol)
            reward = collateral * self._liquidation_reward.get() // POINTS
            for_pool = collateral - reward
            total_debt = pos.total_debt()
            for symbol in self._assets.symbol_list:
                asset = self._assets[symbol]
                is_collateral = asset.is_collateral()
                active = asset.is_active()
                debt = pos.get_loans(collateral_symbol, symbol)
                if not is_collateral and active and debt > 0:
                    bad_debt = asset.bad_debt.get()
                    asset.bad_debt.set(bad_debt + debt)
                    symbol_debt = debt * asset.priceInLoop() // EXA
                    share = for_pool * symbol_debt // total_debt
                    total_debt -= symbol_debt
                    for_pool -= share  # The share of the collateral for that asset.
                    pool = asset.liquidation_pool.get()
                    asset.liquidation_pool.set(pool + share)
                    pos.clear_loans(collateral_symbol, symbol)

            pos.set_collateral_amt(collateral_symbol, 0)
            self._send_token(collateral_symbol, self.msg.sender, reward, "Liquidation reward of")
            self.check_dead_markets()
            self._positions.remove_nonzero(pos_id)
            self.Liquidate(_owner, collateral, f'{collateral} liquidated from {_owner}')

    def check_dead_markets(self) -> None:
        """
        Checks if any of the assets have changed Dead Market status and updates
        them accordingly.
        """
        for collateral_symbol in self._assets.active_collateral_list:
            for symbol in self._assets.symbol_list:
                self._assets[symbol].is_dead(collateral_symbol)

    def _send_token(self, _token: str, _to: Address, _amount: int, msg: str, _data: bytes = None) -> None:
        """
        Sends IRC2 token to an address.
        :param _token: Token symbol.
        :type _token: str
        :param _to: Token destination address.
        :type _to: :class:`iconservice.base.address.Address`
        :param _amount: Number of tokens sent.
        :type _amount: int
        :param msg: Message for the event log.
        :type msg: str
        :param _data: data to sent through token transfer.
        :type _data: bytes
        """
        if _data is None:
            _data = b'None'
        address = self._assets[_token].get_address()
        try:
            token_score = self.create_interface_score(address, TokenInterface)
            token_score.transfer(_to, _amount, _data)
            self.TokenTransfer(_to, _amount, f'{msg} {_amount} {_token} sent to {_to}.')
        except Exception:
            revert(f'{TAG}: {_amount} {_token} not sent to {_to}. ')

    def fallback(self):
        pass

    # --------------------------------------------------------------------------
    #   SETTERS AND GETTERS
    # --------------------------------------------------------------------------

    @external
    @only_owner
    def setGovernance(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._governance.set(_address)

    @external
    @only_admin
    def setRebalance(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._rebalance.set(_address)

    @external
    @only_admin
    def setDex(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._dex.set(_address)

    @external
    @only_governance
    def setAdmin(self, _admin: Address) -> None:
        self._admin.set(_admin)

    @external
    @only_admin
    def setDividends(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._dividends.set(_address)

    @external
    @only_admin
    def setReserve(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._reserve.set(_address)

    @external
    @only_admin
    def setRewards(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._rewards.set(_address)

    @external
    @only_admin
    def setStaking(self, _address: Address) -> None:
        if not _address.is_contract:
            revert(f"{TAG}: Address provided is an EOA address. A contract address is required.")
        self._staking.set(_address)

    @external
    @only_admin
    def setMiningRatio(self, _ratio: int) -> None:
        self._mining_ratio.set(_ratio)

    @external
    @only_admin
    def setLockingRatio(self, _ratio: int) -> None:
        self._locking_ratio.set(_ratio)

    @external
    @only_admin
    def setLiquidationRatio(self, _ratio: int) -> None:
        self._liquidation_ratio.set(_ratio)

    @external
    @only_admin
    def setOriginationFee(self, _fee: int) -> None:
        self._origination_fee.set(_fee)

    @external
    @only_admin
    def setRedemptionFee(self, _fee: int) -> None:
        self._redemption_fee.set(_fee)

    @external
    @only_admin
    def setRetirementBonus(self, _points: int) -> None:
        self._retirement_bonus.set(_points)

    @external
    @only_admin
    def setLiquidationReward(self, _points: int) -> None:
        self._liquidation_reward.set(_points)

    @external
    @only_admin
    def setNewLoanMinimum(self, _minimum: int) -> None:
        self._new_loan_minimum.set(_minimum)

    @external
    @only_admin
    def setMinMiningDebt(self, _minimum: int) -> None:
        self._min_mining_debt.set(_minimum)

    @external
    @only_governance
    def setTimeOffset(self, _delta_time: int) -> None:
        self._time_offset.set(_delta_time)

    @external
    @only_admin
    def setMaxRetirePercent(self, _value: int) -> None:
        if not 0 <= _value <= 10000:
            revert(f'Input parameter must be in the range 0 to 10000 points.')
        self._max_retire_percent.set(_value)

    @external
    @only_admin
    def setRedeemBatchSize(self, _value: int) -> None:
        self._redeem_batch.set(_value)

    @external(readonly=True)
    def getParameters(self) -> dict:
        return {
            "admin": self._admin.get(),
            "governance": self._governance.get(),
            "dividends": self._dividends.get(),
            "reserve_fund": self._reserve.get(),
            "rewards": self._rewards.get(),
            "staking": self._staking.get(),
            "mining ratio": self._mining_ratio.get(),
            "locking ratio": self._locking_ratio.get(),
            "liquidation ratio": self._liquidation_ratio.get(),
            "origination fee": self._origination_fee.get(),
            "redemption fee": self._redemption_fee.get(),
            "liquidation reward": self._liquidation_reward.get(),
            "new loan minimum": self._new_loan_minimum.get(),
            "min mining debt": self._min_mining_debt.get(),
            "max div debt length": self._max_debts_list_length.get(),
            "time offset": self._time_offset.get(),
            "redeem batch size": self._redeem_batch.get(),
            "retire percent max": self._max_retire_percent.get()
        }

    # --------------------------------------------------------------------------
    #   EVENT LOGS
    # --------------------------------------------------------------------------

    @eventlog(indexed=1)
    def ContractActive(self, _contract: str, _state: str):
        pass

    @eventlog(indexed=1)
    def AssetActive(self, _asset: str, _state: str):
        pass

    @eventlog(indexed=2)
    def TokenTransfer(self, recipient: Address, amount: int, note: str):
        pass

    @eventlog(indexed=3)
    def AssetAdded(self, account: Address, symbol: str, is_collateral: bool):
        pass

    @eventlog(indexed=2)
    def CollateralReceived(self, account: Address, symbol: str, value: int):
        pass

    @eventlog(indexed=3)
    def OriginateLoan(self, recipient: Address, symbol: str, amount: int, note: str):
        pass

    @eventlog(indexed=3)
    def LoanRepaid(self, account: Address, symbol: str, amount: int, note: str):
        pass

    @eventlog(indexed=3)
    def BadDebtRetired(self, account: Address, symbol: str, amount: int, sicx_received: int):
        pass

    @eventlog(indexed=2)
    def Liquidate(self, account: Address, amount: int, note: str):
        pass

    @eventlog(indexed=3)
    def FeePaid(self, symbol: str, amount: int, type: str):
        pass

    @eventlog(indexed=2)
    def Rebalance(self, account: Address, symbol: str, change_in_pos: str,
                  total_batch_debt: int):
        pass

    @eventlog(indexed=2)
    def PositionStanding(self, address: Address, standing: str,
                         total_collateral: int, total_debt: int):
        pass

    @eventlog(indexed=1)
    def Snapshot(self, _id: int):
        """
        Emitted as a new snapshot is generated.
        :param _id: ID of the snapshot.
        """
        pass
