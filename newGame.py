

def newGameReset(gameObj):
    playAgain = input(f"Would you like to play again?\ny = yes\t\tn = no\n>  ")
    try:
        playAgain = playAgain.lower()
    except:
        playAgain = "error"
    if playAgain == "y":
        return gameObj()
    elif playAgain == "n":
        print("Thanks for playing!")
        return
    else:
        print("Invalid option. Please choose y or n.")
        return newGameReset(gameObj)




#module for resetting games. Testing referencing other files.