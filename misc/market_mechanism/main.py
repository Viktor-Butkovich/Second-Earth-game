import status, random
from typing import List, Tuple


class owner:
    def __init__(
        self,
        seller: bool,
        num_participants: int,
        price: float,
        production: int,
        name: str = None,
    ) -> None:
        self.name: str = self.generate_name(name)
        self.seller: bool = seller
        self.price: float = price
        self.num_participants: int = num_participants
        self.looking_for_better_deal: bool = False
        self.production: int = production
        status.owners.append(self)
        if self.seller:
            status.sellers.append(self)
        else:
            status.buyers.append(self)

    def generate_name(self, preset_name: str = None) -> str:
        if preset_name:
            name = preset_name
        else:
            name = random.choice(status.first_names) + random.choice(status.last_names)
            while name in status.owner_names:
                name = random.choice(status.first_names) + random.choice(
                    status.last_names
                )
        status.owner_names.append(name)
        return name

    def remove_participants(self, quantity: int) -> None:
        self.num_participants -= quantity
        if self.num_participants <= 0 and self in status.owners:
            if self.seller:
                print(f"{self.name} has no more to sell")
            else:
                print(f"{self.name} has no more to buy")
            self.remove()

    def remove(self) -> None:
        # if self.num_participants > 0:
        participants = open("participants.txt", "a")
        participants.write(
            f"{int(self.seller)} {self.num_participants + self.production} {self.price} {self.production} {self.name}\n"
        )
        participants.close()
        if self.seller:
            status.sellers.remove(self)
        else:
            status.buyers.remove(self)
        status.owners.remove(self)

    def check_better_deal(self) -> None:
        if random.randrange(1, 7) >= 4:
            self.looking_for_better_deal = True
            self.worsen_price()
            print(f"{self.name} is now looking for a better deal for {self.price}")

    def improve_price(self) -> None:
        if self.seller:
            self.price -= status.price_increment
        else:
            self.price += status.price_increment
        if self.price < 0.1:
            self.price = 0.1
        self.price = round(self.price, 1)

    def worsen_price(self) -> None:
        if self.seller:
            self.price += status.price_increment
        else:
            self.price -= status.price_increment
        if self.price < 0.1:
            self.price = 0.1
        self.price = round(self.price, 1)

    def print_summary(self) -> None:
        if self.seller:
            print(
                f"{self.name} wants to sell {self.num_participants} for {self.price} each",
                end="",
            )
        else:
            print(
                f"{self.name} wants to buy {self.num_participants} for {self.price} each",
                end="",
            )
        if self.looking_for_better_deal:
            print(" (looking for better deal)")
        else:
            print()

    def __str__(self) -> str:
        return self.name


def get_random_participant() -> Tuple[owner, int]:
    # owner A1 has 5 participants, and owner A2 has 1 participant
    num_participants = 0
    for current_owner in status.owners:
        num_participants += current_owner.num_participants
    chosen_participant = random.randrange(
        num_participants
    )  # Could choose participant from 0 to 5
    for current_owner in status.owners:
        if chosen_participant >= current_owner.num_participants:
            chosen_participant -= current_owner.num_participants
        else:
            return (current_owner, chosen_participant)


def print_total_owners():
    num_buying = 0
    for current_buyer in status.buyers:
        num_buying += current_buyer.num_participants
    num_selling = 0
    for current_seller in status.sellers:
        num_selling += current_seller.num_participants
    print(f"{len(status.buyers)} buyers want to buy a total of {num_buying}")
    print(f"{len(status.sellers)} sellers want to sell a total of {num_selling}")
    print()


def print_summary():
    print(f"Round {status.round}: ")
    print_total_owners()
    for current_buyer in status.buyers:
        current_buyer.print_summary()
    for current_seller in status.sellers:
        current_seller.print_summary()
    print()


def conduct_round() -> bool:
    for i in range(10):
        print()
    print_summary()
    if status.buyers and status.sellers:
        participant_1: Tuple[owner, int] = get_random_participant()
        participant_2: Tuple[owner, int] = get_random_participant()
        if participant_1[0].seller:
            print(
                f"Participant 1: seller {participant_1[1]} of {participant_1[0].name} for {participant_1[0].price}"
            )
        else:
            print(
                f"Participant 1: buyer {participant_1[1]} of {participant_1[0].name} for {participant_1[0].price}"
            )
        if participant_2[0].seller:
            print(
                f"Participant 2: seller {participant_2[1]} of {participant_2[0].name} for {participant_2[0].price}"
            )
        else:
            print(
                f"Participant 2: buyer {participant_2[1]} of {participant_2[0].name} for {participant_2[0].price}"
            )
        print()
        transaction = False
        if participant_1[0].seller != participant_2[0].seller:
            if participant_1[0].seller:
                seller: Tuple[owner, int] = participant_1
                buyer: Tuple[owner, int] = participant_2
            else:
                seller: Tuple[owner, int] = participant_2
                buyer: Tuple[owner, int] = participant_1
            seller_owner: owner = seller[0]
            buyer_owner: owner = buyer[0]
            if buyer_owner.price >= seller_owner.price:
                transaction = True
        if transaction:
            quantity = 1
            while (
                random.randrange(1, 7) >= 2
                and quantity < buyer_owner.num_participants
                and quantity < seller_owner.num_participants
            ):
                quantity += 1
            print(
                f"{buyer_owner.name} bought {quantity} from {seller_owner.name} for {seller_owner.price} each"
            )
            total_price = status.total_sold * status.average_price
            total_price += quantity * seller_owner.price
            status.total_sold += quantity
            status.average_price = round(total_price / status.total_sold, 3)
            buyer_owner.remove_participants(quantity)
            seller_owner.remove_participants(quantity)
            if buyer_owner in status.buyers:
                buyer_owner.check_better_deal()
            if seller_owner in status.sellers:
                seller_owner.check_better_deal()
        else:
            for current_owner in [participant_1[0], participant_2[0]]:
                if current_owner in status.owners:
                    decision = random.randrange(1, 7)
                    if decision == 1:
                        if current_owner.looking_for_better_deal:
                            current_owner.improve_price()
                            print(
                                f"{current_owner.name} failed to find a transaction and stopped looking for a better deal (price returned to {current_owner.price})"
                            )
                            current_owner.looking_for_better_deal = False
                        else:
                            print(
                                f"{current_owner.name} failed to find a transaction and left the market"
                            )
                            current_owner.remove_participants(1)
                    elif decision >= 6 and not current_owner.looking_for_better_deal:
                        current_owner.improve_price()
                        print(
                            f"{current_owner.name} failed to find a transaction and relaxed their price to {current_owner.price}"
                        )
                    else:
                        print(
                            f"{current_owner.name} failed to find a transaction but stayed in the market"
                        )
    elif not status.buyers:
        for current_seller in status.sellers.copy():
            current_seller.remove()
        print("No buyers remaining")
        return False
    else:
        for current_buyer in status.buyers.copy():
            current_buyer.remove()
        print("No sellers remaining")
        return False
    print("")
    print("End of round: ")
    print_summary()
    print()
    print_total_owners()
    print(f"Total sold: {status.total_sold}")
    if status.total_sold > 0:
        print(f"Average sale price: {status.average_price}")
    if not status.skip_input:
        input("Press enter to start the next round.")
    status.round += 1
    return True


if input("Type reset to reset: ") == "reset":
    participants = open("participants.txt", "w")
    participants.write("")
    participants.close()
    test_case = 4
    if test_case == 1:
        owner(
            seller=True, num_participants=100, price=0.5, production=25, name="Seller1"
        )
        owner(
            seller=False, num_participants=100, price=1.5, production=25, name="Buyer1"
        )
        owner(
            seller=True, num_participants=100, price=0.5, production=25, name="Seller2"
        )
        owner(
            seller=False, num_participants=100, price=1.5, production=25, name="Buyer2"
        )
        owner(
            seller=True, num_participants=100, price=0.5, production=25, name="Seller3"
        )
        owner(
            seller=False, num_participants=100, price=1.5, production=25, name="Buyer3"
        )
        owner(
            seller=True, num_participants=100, price=0.5, production=25, name="Seller4"
        )
        owner(
            seller=False, num_participants=100, price=1.5, production=25, name="Buyer4"
        )
    elif test_case == 2:
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller1"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer1"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller2"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer2"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller3"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer3"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller4"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer4"
        )
    elif test_case == 3:
        owner(
            seller=True, num_participants=100, price=1.5, production=250, name="Seller1"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer1"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=250, name="Seller2"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer2"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=250, name="Seller3"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer3"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=250, name="Seller4"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=25, name="Buyer4"
        )
    elif test_case == 4:
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller1"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=250, name="Buyer1"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller2"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=250, name="Buyer2"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller3"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=250, name="Buyer3"
        )
        owner(
            seller=True, num_participants=100, price=1.5, production=25, name="Seller4"
        )
        owner(
            seller=False, num_participants=100, price=0.5, production=250, name="Buyer4"
        )
    print_summary()
else:
    participants = open("participants.txt", "r")
    for line in participants:
        current_list = line.strip().split()
        owner(
            bool(int(current_list[0])),
            int(current_list[1]),
            float(current_list[2]),
            int(current_list[3]),
            current_list[4],
        )
    print_summary()
    participants.close()
    participants = open("participants.txt", "w")
    participants.write("")
    participants.close()

input_str = input("Type skip to skip to the end: ")
status.skip_input = input_str == "skip"
while conduct_round():
    print()
print()
print_summary()
print(f"Total sold: {status.total_sold}")
if status.total_sold > 0:
    print(f"Average sale price: {status.average_price}")
print()

"""
Single commodity, some number of buyers and sellers, each of which has a certain demand/supply amount to buy/sell
Each item being sold acts as a market participant with a buyer/seller it is owned buy - each one with the same owner has the same price
Each exchange requires a willing buyer and willing seller, which are each market participants
Each seller begins trading with a selling price, and each buyer starts with a buying price
At start of round of trade, check that there is at least 1 willing buyer and seller, otherwise end trading
    Then, choose 2 random distinct participants
        If selected buyer and seller and buyer's price is >= seller's price, transaction occurs - exchange money/item and both participants drop out
            If transaction occurs, repeatedly roll a D6 - on 2+, increase quantity of transaction at the same price, if both owners have more participants
            After transaction, roll a D6 - on 4+, participant's owner changes price to be less favorable to other side - raise price if seller, lower price if buyer
                If this occurs, owner enters looking for a better deal state - if would leave on no transaction, instead leave state and revert price
        If no transaction occurred, roll 1D6 for both participants - if rolled a 1, stop trading (if not looking for better deal)
            On 2-3, do nothing. On 4+, lower price if seller, raise price if buyer
"""
