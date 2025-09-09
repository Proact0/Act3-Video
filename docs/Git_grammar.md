# git-주요명령어 

## 1. 사용자 정보 설정
```bash
# 사용자 이름 설정
git config --global user.name "이름"

# 사용자 이메일 설정
git config --global user.email 이메일

# 설정 정보 확인
git config --list
```

## 2. 저장소
```bash
# 새로운 git 저장소로 초기화
git init

# 원격 저장소 복제
git clone http://github.com/사용자명/repo.git
```

## 3. 파일 상태 확인
```bash
# working directory 영역 상태 확인
git status
```

## 4. 스테이징, 커밋
```bash
# 파일 하나 추가
git add 파일명

# 전체 파일 추가
git add .

# 메세지를 포함한 커밋
git commit -m "커밋 메세지"
```

## 5. 브랜치

```bash
# 브랜치의 이름을 chicken으로 칭함

# 브랜치 목록 확인
git branch

# 새 브랜치 생성
git branch chicken

# 브랜치 이동
git switch chicken
-> switch 대신 checkout도 됨

# 브랜치 병합
git merge chicken

# 브랜치 삭제
git branch -d chicken

```

## 6. 원격 저장소
```bash
# 원격 저장소 이름을 origin으로 하겠음.

# 원격 저장소 확인
git remote -v

# 원격 저장소 추가
git remote add origin [원격저장소주소]

# 원격 저장소 push
git push origin master
-> switch 대신 checkout도 됨

# 원격 저장소 pull
git pull origin master

```

## 7. 되돌리기, 취소
```bash
# 커밋을 soft reset (변경사항 유지)
git reset --soft 커밋해시

# 커밋을 hard reset (변경사항 삭제)
git reset --hard 커밋해시

# 특정 커밋 되돌리기 (이력에 남음)
git revert 커밋해시

```

## 8. 로그옵션
```bash
# git log 정보 확인하기
git log -p

# log 정보 한줄로 확인하기
git log --oneline

```



