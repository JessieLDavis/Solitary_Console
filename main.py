# import random
from datetime import datetime
from random import shuffle
from newGame import newGameReset

# def Solitare():
class Card():
    def __init__(self, cardColorRed,cardSuit,cardNum,cardWritten):
        self.cardColorRed = cardColorRed
        self.cardSuit = cardSuit
        self.cardNum = cardNum
        self.faceCard = self.set_Face()
        self.cardWritten = cardWritten
        self.shortForm = self.set_shortcut()
        self.playable = False
        self.visible = False
    def set_Face(self):
        try:
            int(self.cardWritten)
            return False
        except:
            return True
    def set_shortcut(self):
        if self.cardNum != 10:
            return f"[{self.cardWritten}-{self.cardSuit[0]}]"
        else:
            return f"[{self.cardWritten}{self.cardSuit[0]}]"
    def __str__(self):
        if self.visible == True:
            return self.shortForm
        else:
            return f"[```]"
    def set_Playable(self,playable):
        if playable == True:
            if self.playable == False:
                self.playable = True
            self.set_Visible(True)
        else:
            self.playable = False
        return
    def set_Visible(self,visible):
        if visible == True:
            self.visible = True
        else:
            self.visible = False
        return
class HouseDeck():
    def __init__(self):
        self.deckList = None
        self.deckPlay = []
        self.deckPlayBoard = {"Col 0": [],"Col 1":[],"Col 2":[],"Col 3":[],"Col 4":[],"Col 5":[],"Col 6":[]}
        self.mainBoard = None
        self.deckHand = []
        self.deckAces = {"heart":[],"diamond":[],"spade":[],"club":[]}
        self.acesBoard = None
        self.handPile = []
        self.handBoard = None
        self.activeHandCard = None
        self.playableList = None
        self.activeHand = []
        self.moveCt = 0
    def make_a_deck(self):
        deckSize = 52
        suitList = ["heart","diamond","spade","club"]
        cardList = [("A",1),("2",2),("3",3),("4",4),("5",5),("6",6),("7",7),("8",8),("9",9),("10",10),("J",11),("Q",12),("K",13)]
        mainDeckList = []
        for suit in suitList:
            if suit == "heart" or suit == "diamond":
                cardColorRed = True
            else:
                cardColorRed = False
            for cardinstance in cardList:
                cardWritten = cardinstance[0]
                cardNum = cardinstance[1]
                cardFinal = Card(cardColorRed,suit,cardNum,cardWritten)
                mainDeckList.append(cardFinal)
        # print(mainDeckList)
        return mainDeckList
    def shuffle_deck(self,deckList,redoShuffle=False):
        deckSize = len(deckList)
        finalDeckList = []
        finalTimeCounter = 2
        if deckSize > 1:
            if redoShuffle == False or deckSize <4:
                deckSplit = int(deckSize/2)
            else:
                deckSplit = int(deckSize/4)
            tempDeckA = deckList[:deckSplit]
            tempDeckB = deckList[deckSplit:]
            if len(tempDeckB) > deckSplit+1:
                tempDeckC = deckList[deckSplit:]
                tempDeckB = deckList[:deckSplit]
                if len(tempDeckC) > deckSplit:
                    tempDeckD = deckList[deckSplit:]
                    tempDeckC = deckList[:deckSplit]
                    list3 = [item for sublist in zip(tempDeckD, tempDeckB) for item in sublist]
                    list4 = [item for sublist in zip(tempDeckA, tempDeckC) for item in sublist]
                    finalDeckList = [item for sublist in zip(list3, list4) for item in sublist]
            else:
                finalDeckList = [item for sublist in zip(tempDeckB, tempDeckA) for item in sublist]
                print(len(finalDeckList))
        else:
            print("No shuffle possible.")
            return deckList
        shuffle(finalDeckList)
        if finalDeckList == deckList:
            self.shuffle_deck(deckList,True)
        else:
            print("Shuffle complete.")
            # print(finalDeckList)
            return finalDeckList
    def deal_Hand(self,flipIncr=3):
        if self.handPile != []:
            for cardObj in self.handPile:
                if cardObj.playable == False:
                    cardObj.set_Playable(False)
        if self.deckHand != []:
            if len(self.deckHand) >flipIncr:
                activeHand = self.deckHand[:flipIncr]
                for cardObj in activeHand:
                    self.deckHand.remove(cardObj)
            elif len(self.deckHand) <=flipIncr:
                activeHand = self.deckHand
                self.deckHand = []
            for cardObj in activeHand:
                cardObj.set_Visible(True)
            activeHand[-1].set_Playable(True)
            self.handPile += activeHand
            self.activeHandCard = activeHand[-1]
            self.activeHand = activeHand
            self.moveCt +=1
        else:
            if self.deckHand == [] and self.handPile == []:
                print("Nothing to draw.")
                self.moveCt +=1
                return
            self.deckHand = self.handPile.copy()
            for cardObj in self.deckHand:
                cardObj.set_Playable(False)
            self.handPile = []
            self.activeHand = []
            self.activeHandCard = None
            self.deal_Hand()
    def set_PlayableList(self,depth=0):
        if depth == 0: #only the lowest level
            playableList = []
            if self.activeHandCard != None:
                playableList.append(self.activeHandCard)
            playFieldList = [self.deckAces,self.deckPlayBoard]
            for listing in playFieldList:
                for col,cardList in listing.items():
                    if len(cardList) != 0:
                        playableList.append(cardList[-1])
                    else:
                        pass
            self.playableList = playableList
            return
        elif depth == 1:
            playableList = []
            if self.activeHandCard != None:
                playableList.append(self.activeHandCard)
            for col,cardList in self.deckAces.items():
                if len(cardList) != 0:
                    playableList.append(cardList[-1])
                else:
                    pass
            for col,cardList in self.deckPlayBoard.items():
                if len(cardList) != 0:
                    for cardObj in cardList:
                        if cardObj.visible == True:
                            playableList.append(cardObj)
                else:
                    pass
            self.playableList = playableList
            return
        else:
            playableList = {}
            for col, cardList in self.deckPlayBoard.items():
                if len(cardList) != 0:
                    playableList[col] = cardList[-1]
                else:
                    pass
            self.playableList = playableList
            return playableList
    def set_Board(self):
        self.deckPlay = self.shuffle_deck(self.deckList)
        playArea = self.deckPlay[:28]
        counterCol = 0
        originalNum = 7
        self.deckPlayBoard = {"Col 0": [],"Col 1":[],"Col 2":[],"Col 3":[],"Col 4":[],"Col 5":[],"Col 6":[]}
        sortedDeck = [[0],[1,7],[2,8,13],[3,9,14,18],[4,10,15,19,22],[5,11,16,20,23,25],[6,12,17,21,24,26,27]]
        for k,v in self.deckPlayBoard.items():
            for num in sortedDeck[counterCol]:
                v.append(playArea[num])
            v[-1].set_Playable(True) #card object
            counterCol +=1
        # print(self.deckPlayBoard)
        self.deckHand = self.deckPlay[28:]
        return
    def check_AutoComplete(self):
        autoComplete_Avail = True
        if self.deckHand != [] or self.handPile != []:
            autoComplete_Avail = False
        for col, cardList in self.deckPlayBoard.items():
            for cardObj in cardList:
                if cardObj.visible == False:
                    autoComplete_Avail = False
                    break
        return autoComplete_Avail
    def check_ValidMoveAces(self,cardMoving):
        try:
            cardPresent = self.deckAces[cardMoving.cardSuit][-1]
        except IndexError:
            cardPresent = None
        if cardPresent == None and cardMoving.cardNum == 1:
            self.deckAces[cardMoving.cardSuit].append(cardMoving)
            print("Ace added to top of board.")
            return True
        elif cardPresent == None and cardMoving.cardNum != 1:
            print("Viable move not found")
            return
        if cardPresent.cardSuit == cardMoving.cardSuit and cardMoving.cardNum == (cardPresent.cardNum+1):
            self.deckAces[cardMoving.cardSuit].append(cardMoving)
            print(f"{cardMoving} moved to {cardPresent} on top of board")
            cardPresent.set_Visible(False)
            return True
        print("Viable move not found.")
        return False
    def check_ValidMoveBoard(self,cardMoving,colName):
        try:
            cardMovingTarget = cardMoving[0]
        except:
            cardMovingTarget = cardMoving
        try:
            columnContents = self.deckPlayBoard[colName]
        except KeyError:
            print("Invalid column number.")
            return False
        try:
            cardPresent = columnContents[-1]
            if cardPresent.cardColorRed != cardMovingTarget.cardColorRed and cardPresent.cardNum == (cardMovingTarget.cardNum+1):
                if cardMoving != cardMovingTarget:
                    for cardObj in cardMoving:
                        self.deckPlayBoard[colName].append(cardObj)
                else:
                    self.deckPlayBoard[colName].append(cardMoving)
                print(f"{cardMovingTarget} moved to {colName}")
                return True
        except IndexError:
            if cardMoving != cardMovingTarget:
                if cardMovingTarget.cardNum == 13:
                    for cardObj in cardMoving:
                        self.deckPlayBoard[colName].append(cardObj)
                    print(f"{cardMovingTarget} moved to {colName}")
                    return True
            else:
                if cardMoving.cardNum == 13:
                    self.deckPlayBoard[colName].append(cardMoving)
                    print(f"{cardMovingTarget} moved to {colName}")
                    return True
                print("Only Kings can move to empty columns.")
        print("Viable move not found.")
        return False
    def check_Win(self):
        checkAces = True
        for suit,cardList in self.deckAces.items():
            if len(cardList) != 13:
                checkAces = False
                return False
        print("Congrats!")
        return True
    def resolve_Move(self,movingLoc,cardMoving,cardMovingPack):
        if cardMoving == self.activeHandCard:
            self.handPile.remove(cardMoving)
            try:
                self.activeHandCard = self.handPile[-1]
                self.activeHandCard.set_Playable(True)
            except IndexError:
                self.activeHandCard = None
        else:
            if movingLoc in ["heart","diamond","club","spade"]:
                self.deckAces[movingLoc].remove(cardMoving)
            elif movingLoc == "hand":
                self.handPile.remove(cardMoving)
                try:
                    self.activeHandCard = self.handPile[-1]
                    self.activeHandCard.set_Playable(True)
                except IndexError:
                    self.activeHandCard = None
            else:
                for cardObj in cardMovingPack:
                    self.deckPlayBoard[movingLoc].remove(cardObj)
                if len(self.deckPlayBoard[movingLoc]) != 0:
                    self.deckPlayBoard[movingLoc][-1].set_Playable(True)
        self.set_gameBoard()
        self.moveCt += 1
    def run_AutoComplete(self):
        boardList = list(self.deckPlayBoard.values())
        winVariable = self.check_Win()
        while winVariable == False:
            checkList = self.set_PlayableList(2)
            for col, cardObj in checkList.items():
                confirmation = self.check_ValidMoveAces(cardObj)
                cardMovingPack = [cardObj]
                if confirmation == True:
                    self.resolve_Move(col,cardObj,cardMovingPack)
            self.set_gameBoard()
            self.show_acesBoard()
            winVariable = self.check_Win()
        return
    def check_cardChoice(self,cardMovingOpt):
        cardMoveWrit = cardMovingOpt[:2]
        if cardMoveWrit[1] == "-":
            cardMoveWrit = cardMoveWrit[0]
        cardMoveSuit = cardMovingOpt[-1]
        cardMoving = None
        cardMovingPack = []
        for cardObj in self.deckList:
            if cardObj.cardWritten == cardMoveWrit and cardObj.cardSuit[0].lower() == cardMoveSuit:
                if cardObj.playable == True:
                    cardMoving = cardObj
                    if cardMoving == self.activeHandCard:
                        cardMovingPack = [cardMoving]
                        cardMovingLoc = "hand"
                        return cardMovingLoc, cardMoving, cardMovingPack
                    cardMovingPack = [cardMoving]
                    for col,cardList in self.deckAces.items():
                        if cardObj in cardList:
                            cardMovingLoc = col
                            return cardMovingLoc, cardMoving, cardMovingPack
                    for col,cardList in self.deckPlayBoard.items():
                        if cardObj in cardList:
                            cardMovingLoc = col
                            begin = False
                            for cardOb in cardList:
                                if cardOb != cardMoving:
                                    if begin == False:
                                        pass
                                    else:
                                        cardMovingPack.append(cardOb)
                                else:
                                    begin = True
                            return cardMovingLoc, cardMoving, cardMovingPack
                else:
                    print("Selected card not playable")
                    return
        if cardMoving == None:
            print("Card not found")
            return

    def set_AcesBoard(self):
        acesBoard = f"[<H>][<D>][<S>][<C>]\n"
        for suit,cardList in self.deckAces.items():
            if len(cardList) == 0:
                acesBoard+=f"[---]"
            else:
                acesBoard+=cardList[-1].shortForm
        acesBoard += f"\n\n"
        self.acesBoard = acesBoard
        return

    def set_MainBoard(self):
        # print("[<0>][<1>][<2>][<3>][<4>][<5>][<6>]")
        boardList = list(self.deckPlayBoard.values())
        controlNum = 0
        for entry in boardList:
            if len(entry) > controlNum:
                controlNum = len(entry)
        deckString = f"[<0>][<1>][<2>][<3>][<4>][<5>][<6>]\n"
        for i in range(controlNum):
            rowString = ""
            for col in boardList:
                try:
                    listing = col[i]
                    if listing== None:
                        rowString += "[---]"
                    else:
                        rowString += f"{listing}"
                except IndexError:
                    rowString += f"     "
            deckString += (rowString + f"\n")
        self.mainBoard = deckString
        return
    def set_HandBoard(self):
        #[DECK][--][---][---][^^^][--][PILE]
        #[-##-][--][!!!][!!!][!!!][--][-##-]
        if self.deckHand == None:
            deckEntry = f"[-00-]"
        elif len(self.deckHand) >= 10:
            deckEntry = f"[-{len(self.deckHand)}-]"
        else:
            deckEntry = f"[-0{len(self.deckHand)}-]"
        if self.handPile == None:
            pileEntry = f"[-00-]"
        elif len(self.handPile) >= 10:
            pileEntry = f"[-{len(self.handPile)}-]"
        else:
            pileEntry = f"[-0{len(self.handPile)}-]"
        if self.handPile == None:
            activeString = f" "
        elif len(self.handPile) >= 3:
            activeHand = self.handPile[-3:]
            activeString = f"{activeHand[0]}{activeHand[1]}{activeHand[2]}"
        else:
            emptySpots = 3-len(self.handPile)
            activeString = f""
            if len(self.handPile) != 0:
                for cardObj in self.handPile:
                    activeString += f"{cardObj}"
            for num in range(emptySpots):
                activeString += f"     "
        self.handBoard = f"[DECK]  [---][---][^^^]  [PILE]\n{deckEntry}  {activeString}  {pileEntry}\n"
        return
    
    def show_gameBoard(self):
        print(self.acesBoard,self.mainBoard,self.handBoard,sep="\n")
        return
    
    def set_gameBoard(self):
        self.set_AcesBoard()
        self.set_MainBoard()
        self.set_HandBoard()

    def show_acesBoard(self):
        print(self.acesBoard)
        return

def playing(startVal,gameDeck):
    if gameDeck.acesBoard == None:
        gameDeck.set_gameBoard()
        gameDeck.show_gameBoard()
    else:
        gameDeck.show_gameBoard()
    if gameDeck.deckHand == [] and gameDeck.handPile == []:
        if gameDeck.check_AutoComplete() == True:
            userInput = input("Options:\n quit | play | autocomplete \n>  ").lower()
        else:
            userInput = input("Options:\n quit | play\n>  ").lower()
    else:
        userInput = input("Options:\n quit | draw | play\n>  ").lower()
    if userInput == "quit":
        startVal = "finish"
        return startVal
    elif userInput == "autocomplete":
        if gameDeck.check_AutoComplete() == True:
            gameDeck.run_AutoComplete()
            startVal = "finish"
            return startVal
    elif userInput == "draw":
        gameDeck.deal_Hand()
        gameDeck.set_HandBoard()
    elif userInput == "play":
        userInput = input("h = Play from Hand | b = Play from Board | OR Enter Card Name\n>  ")
        if userInput.lower() == "h":
            if gameDeck.activeHandCard != None:
                cardMoving = gameDeck.activeHandCard
                cardMovingLoc = "hand"
                cardMovingPack = [cardMoving]
            else:
                print("No card in hand")
                return
        else:
            if userInput.lower() == "b":
                cardMovingOpt = input("Please type name of card as seen on screen within the brackets. (Ex: 10h,K-d,A-s,5-d)\n>  ") #need to change orientation
            else:
                cardMovingOpt = userInput
            if len(cardMovingOpt) != 3:
                print("Invalid choice")
                return
            results = gameDeck.check_cardChoice(cardMovingOpt)
            if results != None:
                cardMovingLoc, cardMoving, cardMovingPack = gameDeck.check_cardChoice(cardMovingOpt)
            else:
                print("Error finding card.")
                return
        userInput = input(f"{cardMoving} selected.\nWhere would you like to move card to?\nAces board or main Board? (Type a column number to quick move)\na/b >  ")
        if userInput.lower() == "a":
            #check if card is trapped.
            gameDeck.set_PlayableList(0)
            if cardMoving not in gameDeck.playableList:
                print("Selected card cannot be moved to aces. Move other cards first.")
                return
            elif type(cardMovingPack) == list and len(cardMovingPack)>1:
                print("Only one card can be moved to the aces deck at a time.")
                return
            else:
                confirmation = gameDeck.check_ValidMoveAces(cardMoving)
        else:
            if userInput.lower() == "b":
                gameDeck.set_PlayableList(1)
                print(gameDeck.mainBoard)
                userInput = input(f"Please type the column number you would like to move {cardMoving} to.\n>  ")
            else:
                try:
                    gameDeck.set_PlayableList(1)
                    userInput = int(userInput)
                except ValueError:
                    print("Invalid Input")
                    return

            if len(cardMovingPack) > 1:
                cardMoving = cardMovingPack
            colName = f"Col {userInput}"
            confirmation = gameDeck.check_ValidMoveBoard(cardMoving,colName)
        if confirmation == True:
            #remove cardMoving from whatever list it was in
            gameDeck.resolve_Move(cardMovingLoc,cardMoving,cardMovingPack)
            print("Move complete.")
            if gameDeck.check_Win() == True:
                startVal = "finish"
                return startVal
            return
        else:
            print("Move could not complete.")
            return
        

#[<H>][<D>][<S>][<C>]
#[10h][10h][10h][10h]
#[<0>][<1>][<2>][<3>][<4>][<5>][<6>]
#[---][```][---][---][---][---][---]





#[DECK][--][---][---][^^^][--][PILE]
#[-##-][--][!!!][!!!][!!!][--][-##-]
def SolitareMenu():
    print("Solitare\n[][][][]\n")
    # startVal = input("Press x to begin:\n>  ").lower()
    startVal = "x" #testing shortcut
    if startVal == "x":
        startTime = datetime.now()
        gameDeck = HouseDeck()
        gameDeck.deckList = gameDeck.make_a_deck()
        gameDeck.set_Board()
    while startVal == "x":
        testVal = playing(startVal,gameDeck)
        if testVal == "finish":
            startVal = "finish"
    #scores
    finishTime = datetime.now()-startTime
    print(f"Time to complete: {finishTime}\nTotal moves: {gameDeck.moveCt}")
    newGameReset(SolitareMenu)

# def newGameReset(gameObj):
#     playAgain = input(f"Would you like to play again?\ny = yes\t\tn = no\n>  ")
#     try:
#         playAgain = playAgain.lower()
#     except:
#         playAgain = "error"
#     if playAgain == "y":
#         return gameObj()
#     elif playAgain == "n":
#         print("Thanks for playing!")
#         return
#     else:
#         print("Invalid option. Please choose y or n.")
#         return newGameReset(gameObj)
# if __name__ == "__main__":
SolitareMenu()