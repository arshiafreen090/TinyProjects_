import random

'''Making snake, water and gun game using python
Very plain project you can say, well
'''
youDict= {"s":1,"w":-1,"g":0}
reversedDict = {1:"snake", -1:"gun", 0:"water"}

# 1 for snake, -1 for gun and 0 for water 

computer_choice = random.choice([1,-1,0]) 
youstr = input("Enter your choice (snake(s), water(w), gun(g)): ").lower()
you= youDict[youstr]
print(f"You chose {reversedDict[you]}")
print(f"Computer chose {reversedDict[computer_choice]}")

if (computer_choice == you):
    print("It's a tie!")
else:
    if (you == 1 and computer_choice == 0):
        print("You win! Snake drinks water.")
    elif (you == 0 and computer_choice == -1):  
        print("You win! Water douses gun.") 
    elif (you == -1 and computer_choice == 1):
        print("You win! Gun kills snake.")
    else:
        print("You lose!")
    
'''
There is also a way to do this using a single line of code, but I wanted to keep it simple and readable for beginners.
'''
'''
you-computer_choice== 1 or you-computer_choice== -2 is the 

winning condition for the player. so, we can use that to make no. of lines of code less but this is not a good practice for beginners to understand the logic of the game. so, I have kept it simple and readable.
'''
if you-computer_choice== 1 or you-computer_choice== -2:
    print("You win!")
else:
    print("You lose!")
    pass