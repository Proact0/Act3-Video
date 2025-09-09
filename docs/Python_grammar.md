# Python, 핵심 문법 정리

이 문서는 파이썬 프로그래밍의 핵심적인 문법을 정리합니다.

---

## 1. 변수와 자료형

- 변수는 값을 저장하는 공간.

### 1.1. 기본 자료형

```
# 정수 (Integer)
a = 10

# 실수 (Float)
b = 3.14

# 문자열 (String)
c = "Hello, Python!"
d = '파이썬은 쉬워요.'

# 불리언 (Boolean)
e = True
f = False

# 변수의 자료형 확인
print(type(a))  # <class 'int'>
print(type(c))  # <class 'str'>
```

### 1.2. 형 변환

- 자료형을 명시적으로 변환할 수 있다.

```
num_str = "123"
num_int = int(num_str)  # 문자열을 정수로
print(num_int + 1)      # 124

num_float = float(num_int) # 정수를 실수로
print(num_float)         # 123.0

num_again_str = str(num_float) # 실수를 문자열로
print(num_again_str)     # "123.0"

```

## 1.3. 자료구조

### 1.3.1 리스트 (list)

- [] 대괄호를 사용하여 정의함.

```
fruits = ["apple", "banana", "cherry", "apple"]

# 인덱싱 (Indexing)
print(fruits[0])  # "apple"
print(fruits[-1]) # "cherry" (마지막 요소)

# 슬라이싱 (Slicing)
print(fruits[1:3]) # ['banana', 'cherry']

# 요소 추가
fruits.append("orange")
print(fruits) # ['apple', 'banana', 'cherry', 'apple', 'orange']

# 요소 수정
fruits[1] = "blueberry"
print(fruits) # ['apple', 'blueberry', 'cherry', 'apple', 'orange']

# 요소 삭제
del fruits[0]
print(fruits) # ['blueberry', 'cherry', 'apple', 'orange']

```

### 1.3.2 튜플(tuple)

- () 소괄호를 사용해 정의한다. 수정 불가.

```
colors = ("red", "green", "blue")

print(colors[0]) # "red"
# colors[0] = "yellow" # TypeError 발생!

```

### 1.3.3 딕셔너리(dictionary)

- key:value란. 쌍으로 이루어진 데이터를 저장하며 순서가 없다.
- {} 중괄호로 정의

```
person = {
    "name": "Chicken",
    "age": 25,
    "city": "New York"
}

# Key를 이용해 Value에 접근
print(person["name"]) # "Chicken"

# 새로운 Key:Value 쌍 추가
person["job"] = "Developer"
print(person) # {'name': 'Chicken', 'age': 25, 'city': 'New York', 'job': 'Developer'}

# 값 수정
person["age"] = 26
print(person["age"]) # 26

# Key-Value 쌍 삭제
del person["city"]
print(person) # {'name': 'Chicken', 'age': 26, 'job': 'Developer'}

```

### 1.3.4 집합(set)

- 순서가 없고, 중복을 허용하지 않는 자료 구조
- {}중괄호를 사용해 정의. 딕셔너리랑 구분된다.

```
numbers = {1, 2, 3, 2, 4, 5, 1}
print(numbers) # {1, 2, 3, 4, 5} (중복 제거)

# 합집합, 교집합, 차집합 등 집합 연산에 유용
set_a = {1, 2, 3}
set_b = {3, 4, 5}

print(set_a | set_b) # 합집합: {1, 2, 3, 4, 5}
print(set_a & set_b) # 교집합: {3}
print(set_a - set_b) # 차집합: {1, 2}

```

## 2. 주석

- `#` 기호를 사용하여 한 줄 주석을 작성. 주석은 코드 실행에 영향을 주지 않고, 코드에 대한 설명을 추가할 때 사용.

```
# 이 라인은 주석입니다.
x = 5  # 변수 x에 5를 할당.
```

## 3. 입출력 (Input/Output)

- **출력**: `print()` 함수를 사용하여 화면에 값을 출력합니다.
- **입력**: `input()` 함수를 사용하여 사용자로부터 문자열을 입력받습니다.

```
name = input("이름을 입력하세요: ")
print("안녕하세요,", name)

# 숫자를 입력받을 경우 형 변환이 필요합니다.
age = int(input("나이를 입력하세요: "))
print("내년에는", age + 1, "살이 되시는군요.")
```

## 4. 제어문

### 4.1. 조건문 (if, elif, else)

- 조건의 참/거짓에 따라 코드 블록을 실행한다.

```
score = 85

if score >= 90:
    print("A 등급")
elif score >= 80:
    print("B 등급")
else:
    print("C 등급")
```

### 4.2. 반복문 (for, while)

`for` 반복문

- 시퀀스(리스트, 튜플,문자열 등)의 각 항목을 순회한다.

```
# 리스트 순회
items = ["a", "b", "c"]
for item in items:
    print(item)

# range() 함수와 함께 사용
for i in range(5): # 0부터 4까지
    print(i, end=" ") # 0 1 2 3 4
```

`while` 반복문

- 특정조건이 참(true)인 동안 코드를 반복 실행

```
count = 0
while count < 5:
    print(count)
    count += 1 # 이 부분이 없으면 무한 루프에 빠짐
```

## 5. 함수 (Functions)

- `def` 키워드를 사용하여 함수를 정의합니다. 함수는 재사용 가능한 코드 블록입니다.

```python
def add(x, y):
    """두 숫자를 더한 값을 반환하는 함수"""
    return x + y

# 함수 호출
result = add(10, 20)
print(result)  # 30 출력
```

## 6. 클래스(class), 객체(object)

- 클래스는 객체를 생성하기 위한 틀, 객체는 클래스로 부터 만들어진 실체이다. 데이터와 기능을 하나로 묶어 관리할 수 있게 해준다.
- 클래스 내부에 정의된 변수를 속성, 함수를 메서드(method)라고 한다.

```
# 클래스 정의
class Dog:
    # 생성자: 객체가 생성될 때 호출됩니다.
    def __init__(self, name, age):
        self.name = name  # 속성
        self.age = age    # 속성

    # 메서드: 클래스 내부에 정의된 함수
    def bark(self):
        print(f"{self.name}가 멍멍 짖습니다!")

# 객체 생성
my_dog = Dog("바둑이", 3)

# 속성 접근
print(my_dog.name)  # '바둑이' 출력
print(my_dog.age)   # 3 출력

# 메서드 호출
my_dog.bark()       # '바둑이가 멍멍 짖습니다!' 출력
```

## 7. 모듈과 패키지

- 모듈은 파이썬 코드를 담고 있는 파일이며, 패키지는 여러 모듈을 담고 있는 폴더이다. import 키워드를 사용해 다른 파일에 있는 함수나 클래스를 가져와 사용할 수 있다.

```
# 내장 모듈 사용 예시 (math 모듈)
import math

# math 모듈의 sqrt 함수 사용
print(math.sqrt(16))  # 4.0 출력

# 특정 함수만 가져오기
from math import pi

print(pi)  # 3.141592653589793 출력
```
