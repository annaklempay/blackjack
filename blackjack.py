#!/usr/bin/env python3

''' blackjack.py -- written by Anna Klempay (@annaklempay)
    A traditional blackjack game, inspired by a project from Al Sweigart's book,
    'The Big Book of Small Python Projects.' Adapted to include Python dataclasses,
    more options for user input, and other personal customizations.
'''

import dataclasses
import random
import sys
from collections import deque

# Constants - card suits

HEARTS      = chr(9829) # Character 9829 is '♥'
DIAMONDS    = chr(9830) # Character 9830 is '♦'
SPADES      = chr(9824) # Character 9824 is '♠'
CLUBS       = chr(9827) # Character 9827 is '♣'

# Classes

class PokerCard:
    VALUE = {
        11: 'J',
        12: 'Q',
        13: 'K',
        14: 'A',
    }

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.backside = False

    def flip(self):
        self.backside = ~self.backside
        return self

    def display(self):
        ''' Designed to look like an ASCII poker card.
        e.g. A card with a suit of HEARTS and a value of 5 should look like the following:
         ___ 
        |5  |
        | ♥ |
        |__5|
        '''
        if self.backside: # If card is turned on its backside, don't display suit/value
            return [f' ___ ', f'|## |', f'|###|', f'|_##|']
        return [f' ___ ',f'|{PokerCard.VALUE.get(self.value, self.value):<3}|', f'| {self.suit} |', f'|_{PokerCard.VALUE.get(self.value, self.value):>2}|']

class DeckofCards:
    def __init__(self):
        self.cards = deque([])
        for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
            for value in range(2, 15):
                self.cards.append(PokerCard(suit, value))
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.popleft()

    def discard(self, oldcards):
        self.cards.extend(oldcards)

# Functions

def getBet(maxBet):
    '''Ask the player how much they want to bet for this round, with the option to quit.'''
    while True:
        bet = input(f'How much do you want to bet? ($0.50 - ${maxBet:.2f}, or QUIT)\n> ').upper().strip()
        if bet == 'QUIT':
            print('Thanks for playing!')
            sys.exit()
        # User error: bet is outside of range
        bet = float(bet)
        while bet > maxBet or bet < 0.5:
            bet = float(input(f'Please enter an amount in the specified range.\n> '))
        return bet

def displayCards(firstSet, secondSet, showDealer):
    '''Display the cards in each of the players' hands.'''
    if showDealer:
        print(f'DEALER HAND: {handValue(firstSet)}')
        firstSet[0] = firstSet[0].flip()
    else:
        print('DEALER HAND: ???')
    for row in range(4):
        print(' '.join([card.display()[row] for card in firstSet]))

    print(f'\nYOUR HAND: {handValue(secondSet)}')
    for row in range(4):
        print(' '.join([card.display()[row] for card in secondSet]))
    print()

def handValue(cards):
    '''Given a set of cards, calculate the total value.'''
    total = 0
    aces = 0

    # Add value for non-ace cards
    for card in cards:
        if card.value != 14:
            total += min(10, card.value)
        else:
            aces += 1
    
    # Add value for aces
    total += aces # Add 1 for each ace
    for _ in range(aces):
        if total + 10 <= 21: # If another 10 can be added without busting, do so
            total += 10

    return total

def getMove(cards, money, name):
    '''Asks player for their move and returns the move code ('H', 'S', 'D', 'Q').'''
    # Determine possible moves for player
    moves = {'(H)it', '(S)tand'}
    if len(cards) == 2 and money > 0:
        moves.add('(D)ouble down')

    # Get the player's move, looping until correct input
    while True:
        move = input(f'{name}, it\'s your move: ' + ' '.join(moves) + '\n> ').upper().strip()
        if move in ('H', 'S'):
            return move
        if move == 'D' and '(D)ouble down' in moves:
            return move

# Main Function

def main():

    # Print game rules
    print('''Welcome to my blackjack table!

    --- GAME RULES ---
    Try to get as close to 21 without going over.
    Kings, Queens, and Jacks are worth 10 points.
    Aces are worth 1 or 11 points.
    Cards 2 through 10 are worth their face value.
    (H)it to take another card.
    (S)tand to stop taking cards.
    On your first play, you can (D)ouble down to increase your bet
    but must hit exactly one more time before standing.
    In case of a tie, the bet is returned to the player.
    The dealer stops hitting at 17.
    This game does not account for naturals, splitting, or any
    kind of insurance.
    ''')

    # User introduction
    userName = input('What\'s your name, player?\n> ')
    userMoney = float(input('How much money are you playing with today (in dollars)?\n> '))
    print(f'Best of luck, {userName}!\n\n')
    deck = DeckofCards()
    roundcount = 1
 
    while True:
        # Check if the player is out of money and offer chance to buy back in
        if userMoney <= 0:
            print('You\'re out of money!')
            keepPlaying = input('Do you want to buy back in to keep playing? (Y\\N)\n> ').upper().strip()
            # User error: improper selection
            while keepPlaying != 'N' and keepPlaying != 'Y':
                keepPlaying = input(f'Please input \'Y\' to continue playing or \'N\' to quit.\n> ').upper().strip()
            if keepPlaying == 'N':
                print('Thanks for playing!')
                sys.exit()
            moreMoney = float(input('How much money would you like to add to your funds?\n> '))
            # User error: did not meet minimum addition
            while moreMoney < 0.5:
                moreMoney = float(input('Minimum addition is $0.50.\n> ')) 
            userMoney += moreMoney
        
        # Let player enter bet for the first round
        print(f'--- ROUND {roundcount} ---')
        print(f'YOUR FUNDS: ${userMoney:.2f}')
        bet = getBet(userMoney)

        # Deal to the both user and player
        dealerHand = [deck.deal().flip(), deck.deal()]
        userHand = [deck.deal(), deck.deal()]

        # Handle player actions
        print(f'Bet: ${bet:.2f}')
        displayCards(dealerHand, userHand, False)
        while True: # Keep looping until player stands or busts
            
            # Check if the player has lost
            if handValue(userHand) > 21:
                break

            # Check if the player has already won
            if handValue(userHand) == 21:
                break

            # Get the player's move if they have not lost yet
            userMove = getMove(userHand, userMoney - bet, userName)
            if userMove == 'D': # Option to increase their bet to twice the original value
                additionalBet = getBet(min(bet, (userMoney-bet)))
                bet += additionalBet
                print(f'Bet increased to ${bet:.2f}')
                print(f'Bet: ${bet:.2f}')

            if userMove in ('H', 'D'): # If user selected to double down OR hit, they receive another card
                newCard = deck.deal()
                print(f'You drew a {PokerCard.VALUE.get(newCard.value, newCard.value)} of {newCard.suit}!')
                userHand.append(newCard)
                displayCards(dealerHand, userHand, False)

                # Check if the player has lost
                if handValue(userHand) > 21:
                    continue
            
            if userMove in ('S', 'D'):
                break

        # Give the user the opportunity to evaluate
        input('Dealer is up next! Press Enter when ready.')
    
        # Dealer's actions
        if handValue(dealerHand) <= 21:
            while handValue(dealerHand) < 17:
                print('Dealer hits...')
                dealerHand.append(deck.deal())
                displayCards(dealerHand, userHand, False)
                input('Press Enter to continue.')
                if handValue(dealerHand) > 21:
                    break

        # Show final hands
        displayCards(dealerHand, userHand, True)
        finalUserVal = handValue(userHand)
        finalDealVal = handValue(dealerHand)

        # Handle final results
        if finalDealVal > 21:
            print(f'Dealer busts! You win ${bet:.2f}!')
            userMoney += bet
        elif finalUserVal > 21 or finalUserVal < finalDealVal:
            print('You lost!')
            userMoney -= bet
        elif finalUserVal > finalDealVal:
            print(f'You won ${bet:.2f}, {userName}!')
            userMoney += bet
        elif finalUserVal == finalDealVal:
            print('It\'s a tie -- bet is returned to you.')

        # Discard the used cards and move onto next round
        deck.discard(dealerHand + userHand)
        roundcount += 1
        input('Press Enter to continue.')
        print('\n\n')

# Main Exection

if __name__ == '__main__':
    main()
