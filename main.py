import random

ans = [random.randrange(10) for _ in range(4)]


while True:
    num = int(input("Enter a number(0000-9999): "))
    guess = [0] * 4
    digit = 1000
    ACount = 0
    BCount = 0
    guess_used = [False] * 4
    ans_used = [False] * 4

    for i in range(4):
        guess[i] = num // digit
        num %= digit
        digit //= 10
    for i in range(4):
        if guess[i] == ans[i]:
            ACount += 1
            guess_used[i] = True
            ans_used[i] = True

    for i in range(4):
        for j in range(4):
            if guess[i] == ans[j] and i != j and not ans_used[i]:
                BCount += 1
                ans_used[i] = True
    print(f"your guess: {guess} \nA:{ACount} B:{BCount}")
    if ACount == 4:
        print("You guess the correct number!")
        break