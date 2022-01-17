class RebalancePool:
    INITIAL_LTV = 0.5
    def __init__(self):
        self.collateral = 0
        self.loan = 0
        self.tokens = 0
        self._collateralPrice = 0
    
    def deposit(self, collateral, loan):
        self.collateral += collateral
        self.loan += loan

        poolShare = loan
        if self.tokens:
            share = (self.loan/loan) - 1
            poolShare = self.tokens/share
        self.tokens += poolShare

        return poolShare
       
    def sell(self, amount):
        self.collateral -= amount
        self.loan -= amount*self._collateralPrice

    def buy(self, amount):
        self.loan += amount
        self.collateral += amount/self._collateralPrice

    def getRatio(self):
        if self.collateral == 0:
            return self.INITIAL_LTV
        return self.loan/(self.collateral * self._collateralPrice) 
    
    def getPosition(self, poolShareTokens):
        share = poolShareTokens/(self.tokens)
        return self.collateral*share, self.loan*share

class User:
    def __init__(self, address):
        self.address = address
        self.collateral = 0
        self.locked_loan = 0
        self.pool_share_tokens = 0

class Loans:
    def __init__(self):
        self.users = {}
        self.collateralPrice = 1
        self.rebalance_pool = RebalancePool()
        self.rebalance_pool._collateralPrice  =  self.collateralPrice
    
    def get(self, address):
        return self.rebalance_pool.getPosition(self.users[address].pool_share_tokens)

    def setPrice(self,price):
        self.collateralPrice = price
        self.rebalance_pool._collateralPrice  = price

    def depositAndBorrow(self, user, collateral, loan):
        if user.address not in self.users:
            self.users[user.address] = user

        rebalanceCollateral = loan/(self.collateralPrice*self.rebalance_pool.getRatio())
        user.collateral += collateral - rebalanceCollateral
        user.pool_share_tokens += self.rebalance_pool.deposit(rebalanceCollateral, loan)

loans = Loans()
rebalance_pool = loans.rebalance_pool
user1 = User(1)
user2 = User(2)
user3 = User(3)
user4 = User(4)
loans.setPrice(2)
loans.depositAndBorrow(user1, 1000, 100)
loans.depositAndBorrow(user2, 2000, 400)

rebalance_pool.sell(125)

loans.depositAndBorrow(user3, 1000, 100)
rebalance_pool.sell(35)

loans.depositAndBorrow(user4, 1000, 200)


print(loans.get(1))
print(loans.get(2))
print(loans.get(3))
print(loans.get(4))