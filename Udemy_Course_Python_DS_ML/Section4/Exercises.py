# Python Crash Course Exercises
# Python Basics

# 1. ** What is 7 to the power of 4?**
a = 7 ** 4
print(a)

# 2. ** Split this string: s = "Hi there Sam!" into a list. **
s = "Hi there Sam!"
s2 = s.replace("Sam", "dad")  # also replace Sam with dad
s_as_string = s2.split(" ")
print(s_as_string)

# 3. ** Given the variables:
planet = "Earth"
diameter = 12742
# Use .format() to print the following string:      The diameter of Earth is 12742 kilometers. **
print(f"The diameter of %s is %d kilometers" % (planet, diameter))
print("The diameter of {0} is {1} kilometers".format(planet, diameter))

# 4. ** Given this nested list, use indexing to grab the word "hello" **
lst = [1, 2, [3, 4], [5, [100, 200, ['hello']], 23, 11], 1, 7]
print(lst[3][1][2][0])

# 5. ** Given this nested dictionary grab the word "hello". Be prepared, this will be annoying/tricky **
d = {'k1': [1, 2, 3, {'tricky': ['oh', 'man', 'inception', {'target': [1, 2, 3, 'hello']}]}]}
print(d["k1"][3]["tricky"][3]["target"][3])

# 6. ** What is the main difference between a tuple and a list? **
# TUPLES ARE IMMUTABLE WHILE LISTS ARE NOT, THEY ARE DYNAMIC

# 7. ** Create a function that grabs the email website domain from a string in the form: **
domain_str = "user@domain.com"
# **So for example, passing "user@domain.com" would return: domain.com**
def domainGet(domain):
    list_result = domain.split("@")
    return list_result[-1]
print(domainGet(domain_str))

# 8. ** Create a basic function that returns True if the word 'dog' is contained in the input string.
# Don't worry about edge cases like a punctuation being attached to the word dog, but do account for capitalization. **
str_dog = "Is there a dog here?"
def findDog(string_dog):
    list_str = string_dog.split(" ")
    flag = False;
    for elem in list_str:
        if elem == 'dog':
            flag = True
    return flag
print(findDog(str_dog))

# 9. ** Create a function that counts the number of times the word "dog" occurs in a string. Again ignore edge cases. **
str_dog = "This dog runs faster than the other dog dude!"
def countDog(string_dog):
    return string_dog.count("dog")
print(countDog(str_dog))

# 10. ** Use lambda expressions and the filter() function to filter out words from a list that don't start with the letter 's'.
seq = ['soup','dog','salad','cat','great']  # **should be filtered down to: ['soup','salad']
result = list(filter(lambda word: word.startswith('s'), seq))
print(result)

# 11. ### Final Problem
# **You are driving a little too fast, and a police officer stops you. Write a function
#   to return one of 3 possible results: "No ticket", "Small ticket", or "Big Ticket".
#   If your speed is 60 or less, the result is "No Ticket". If speed is between 61
#   and 80 inclusive, the result is "Small Ticket". If speed is 81 or more, the result is "Big Ticket".
#   Unless it is your birthday (encoded as a boolean value in the parameters of the function)
#       -- on your birthday, your speed can be 5 higher in all cases. **

def caught_speeding(speed, is_birthday):
    no_ticket_maximum = 60
    small_ticket_maximum = 80
    big_ticket_minimum =81
    if is_birthday:
        no_ticket_maximum +=5
        small_ticket_maximum +=5
        big_ticket_minimum +=5
    if speed <=no_ticket_maximum:
        return "No ticket"
    elif no_ticket_maximum+1 <= speed <= small_ticket_maximum:
        return "Small Ticket"
    elif speed >= big_ticket_minimum:
        return "Big Ticket"
    return None

print(caught_speeding(81,True))
print(caught_speeding(81,False))