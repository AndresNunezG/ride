Project created with Django [cookiecutter](https://github.com/cookiecutter/cookiecutter-django):

# Ride 

# App architecture

- SOAP: Has its own standart, known for using XML
- REST: Representational State Transfer, the goal is stateless operations. REST relies on the HTTP protocol.
- GraphQL: The most modern, developed by FB. Works like a query language for API's

### SERVICE ORIENTED ARCHITECTURE

- Self-contained
- Black box for users
- Represents an bussiness activity with a specific purpose

### Twelve-Factor App

# Objectives

- Declarative settings
- Clear contract with OS
- Ready to launch
- Reduce difference between environments
- Easy Scale

# Features

## Users

- Sign up (with confirmation email)
- Log in
- User detail
- User update (Base and Profile)

## Circles

- List all the circles (filtering and search)
- Create a new circle
- Circle detail
- Update circle
- List members of a circle
- Join a circle (invitation)
- Member detail
- Remove member
- Get invitations code

# Models

## Users

### Base

- Email
- Username
- Phone number
- First name
- Last name

### Profile

- User (PK)
- Picture
- Biography (about me)
- Rides taken (total)
- Rides offered (total)

### Member

- User (PK)/Profile(PK)
- Circle (PK)
- Circle admin (BOOL)
- Invitations (used/remaining)
- Who invited her/him?
- Rides taken (inside the circle)
- Rides offered (inside the circle)

## Circles (groups)

### Circle

- Name
- Slug name
- About
- Picture
- Members
- Rides taken
- Rides offered
- is it and official circle? (BOOL)
- is it public? (BOOL)
- Has limit if members? (INT)

### Invitation

- Code
- Circle (PK)
- Who made the invitation?
- Who used the invitation?
- When was the invitation used?

## Rides

# Ride

- Who offer the ride?
- When and where was the ride offered?
- In which circle was offered the ride?
- How may sits are available?
- Additional comments
- Rank
- It is active?

# Rank

- Ride (PK)
- Circle (PK)
- Who ranked?
- who is the ranked?
- Rank (1-5)

# by: Andrés Camilo
