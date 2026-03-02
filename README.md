## Pandemic simulation

### Step 1: Define Your Simulation (Before Any Code)
This project demonstrates how individual movement patterns within a city can generate large-scale pandemic dynamics. Even though each person follows simple behavioral rules, their daily movement and local interactions lead to complex infection curves at the city level. The simulation shows how population density directly influences transmission speed, as higher concentrations of agents increase contact frequency and accelerate the spread of disease.

### My Smart City Project: Pandemic simulation

#### 1. The Trigger (Who/What is moving?)
Agents: The person living in the city. 
Each person has:
A health status (susceptibel, infected, Recovered)
A position in the city
A random movement pattern

#### 2. The Observer (What does the city see?)
Distance between the person
The health status of the persons
Number of infected persons in the city


#### 3. The Control Center (The Logic)
If an infected person is closer to an susceptibel person than the inffection radius there is a 50% chance the susceptibel person will be infected
When an infected person is infected in more than 10 days their health status will chance to recovered.


#### 4. The Response (What happens next?)
The persons health status updates
A graph showing the numbers of persons infected
