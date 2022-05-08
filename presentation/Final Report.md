# Final Report: Analyzing Services for Madison WI, St.Louis MO, Minneapolis MN, and Lansing MI


## **Part 1: Introduction**
  For this project, we would like to understand how different services (banks, clinics, dentistries, hospitals, and supermarkets) are distributed in a city and whether people can reach to the same level of services when they take buses. Take Madison as an example, among all the two hundred fifty thousand people living in different census blocks in Madison, how do we know whether anyone from any census blocks can get to the same level of services when they take buses. Services are distributed well in a city if anyone from any place can reach to the same level of services when they take buses. In this project, we are going to explore four different cities: Madison WI, St.Louis MO, Minneapolis MN, Lansing MI.

### **Service Score Calculation**
* The level of services reached is a very subjective term, hence we decided to implement a function to give a score to measure how good services are in an area. A higher score means that the level of services reached is better. 
* We chose to implement a sigmoid function because the sigmoid function has a s-shape. The reason why we prefer a s-shape is that when we reach enough number of services, the score should be kind of flat due to saturation. 
* This function is being used for each census block within a city to find the lowest scores and highest scores of the census block within that city.
```
def get_sigmoid(x):
    return 1/(1+math.e**(-x))

def get_score(area, banks=0, clinics=0, dentists=0,   hospitals=0, supermarkets=0):
    score = get_sigmoid(banks) + get_sigmoid(clinics) + get_sigmoid(hospitals) + get_sigmoid(dentists) + get_sigmoid(supermarkets)
    return score
```


## **Part 2: Four Cities Analysis**
### **Methods:**
* For each city, we used the centroid of each census block as the starting point for SCANanalyzer to run the bus simulator. 
* For the score vs. time graphs, each line represents a centroid in a census block. These centroids are deliberately selected by calculating their services scores for each census block. The ten centroids with the highest service scores mean that these ten census blocks have a lot of services in them. The ten centroids with the lowest service scores mean that these ten census blocks do not have many services in them. Then we used these top ten and bottom ten centroids as starting points to run the bus simulator and find their reachable areas every three hours from Monday to using a elapse time of 30 minutes. In these reachable areas, we determined how many services they could reach and calculate their 
* These census bl census blocks (centroids) with the ten highest and ten lowest service scores. These ten highest and ten lowest services scores are associated with the number of services in each 
* for service score analysis. We 
* The ten highest and ten lowest service scores are calculated by adding up the number of services in a census block

### **Results:**
#### **Madison, Wisconsin**
* Overview of Madison routes network
  
  Here is an overview of all the bus routes in Madison, WI: 
  <img src="madison_routes.png" alt="madison_routes" width="600" height="400">
  In Madison, the route network focuses on hubs at the Capitol Square in downtown Madison and four major transfer points in outer parts of Madison.  Many routes serve downtown Madison and UW-Madison, where traffic usage is high.

  <img src="visual_madison.png" alt="madison heat graph" width="400" height="600">

* For each census blocks, we use the centroids 


* The ten highest scores of census centroids:
|    | label                                                     |   max score |   min score |   median score |
|---:|:----------------------------------------------------------|------------:|------------:|---------------:|
|  0 | 1652 Meadowcrest Lane                                     |     8.63154 |           0 |        4.59358 |
|  1 | SSM Physician Parking Fish Hatchery Road                  |    27.3281  |           0 |       20.3445  |
|  2 | Sheboygan-Segoe Sheboygan Avenue                          |    32.3336  |           0 |       24.2205  |
|  3 | 7109 Colony Drive                                         |    12.7064  |           0 |        7.91297 |
|  4 | Nevin Springs State Fishery and Wildlife Area Cahill Main |     4.52522 |           0 |        0       |
|  5 | American Family Insurance Madison                         |     1.82843 |           0 |        0       |
|  6 | 4147 Terminal Drive                                       |     0       |           0 |        0       |
|  7 | 2998 Columbia Road                                        |    31.7218  |           0 |       26.2291  |
|  8 | 9375 Spirit Street                                        |     0       |           0 |        0       |
|  9 | 6179 Research Park Boulevard                              |    22.2021  |           0 |       16.9148  |

<img src="madison_high.png" alt="madison_high" width="800" height="400">

* The ten lowest scores of census centroids:

|    | label                                                           |   max score |   min score |   median score |
|---:|:----------------------------------------------------------------|------------:|------------:|---------------:|
|  0 | 465 Davies Street                                               |    10.6045  |           0 |        3.78525 |
|  1 | 2133 Keyes Avenue                                               |    25.6982  |           0 |       19.2128  |
|  2 | 410 Pawling Street                                              |    19.2096  |           0 |       17.8433  |
|  3 | 3907 Hynek Road                                                 |    16.9268  |           0 |       16.0026  |
|  4 | 770 Lamont Lane                                                 |     9.77114 |           0 |        4.24737 |
|  5 | 1196 Rowell Street                                              |    27.3281  |           0 |        6.3546  |
|  6 | 1891 Elka Lane                                                  |    14.2808  |           0 |        6.92799 |
|  7 | University of Wisconsin Arboretum - Grady Tract Kirkwall Street |    11.5327  |           0 |        4.8177  |
|  8 | 5498 Regent Street                                              |    17.4869  |           0 |       12.7752  |
|  9 | Odana Hills Golf Course 4635                                    |    19.0319  |           0 |        5.89037 |

<img src="madison_low.png" alt="madison_low" width="800" height="400">

* From above two figures, the highest score line(calcualted by the coverage of services starting from the centroid of the census) of the ten highest scores of census centroids is not much higher than the highest score line of the ten lowest scores of census centroids. The max score for the high census is about 32 while the max score for the low census is about 27.33. It shows that the services of the madison is advanced enough for people from not only high score census but only the low score census to reach services. But high census still have more services to choose through bus transit overall.

* The v tuobaisualization of the Madison census:
<img src="visual_madison.png" alt="visual_madison" width="800" height="400">
The shade of the blue color for each census is based on the coverage services starting from centroid of the census through bus transit. The deeper the color, the more score of the coverage service for the starting centroid point of census. We can found the highest score for the madison is over 40.

#### **St. Louis, Missouri**
* Overview of St. Louis routes network
  Here is an overview of all the bus routes in St. Louis, MO: 
  <img src="stlouis_routes.jpg" alt="stlouis_routes" width="600" height="400">
  In St. Louis, the route network focuses on the census Richmond Heights.

* The ten highest scores of census centroids:

|    | label                                     |   max score |   min score |   median score |
|---:|:------------------------------------------|------------:|------------:|---------------:|
|  0 | Chippewa at Regal Place Chippewa Street   |     14.1783 |           0 |       11.1506  |
|  1 | Lansdowne at Chippewa Lansdowne Avenue    |     10.2808 |           0 |        9.58429 |
|  2 | 6000 Lansdowne Avenue                     |     15.7129 |           0 |        9.66561 |
|  3 | 5406 Wise Avenue                          |     16.7857 |           0 |        4.28971 |
|  4 | 528 South Sarah Street                    |     30.3576 |           0 |       23.9757  |
|  5 | 4444 Forest Park Avenue                   |     33.9023 |           0 |       26.8917  |
|  6 | Grant Medical Clinic 114                  |     26.8042 |           0 |       17.4304  |
|  7 | Saint Nicholas Greek Orthodox Church 4967 |     34.7062 |           0 |       26.5922  |
|  8 | 6254 Mardel Avenue                        |     15.8627 |           0 |        9.66561 |
|  9 | Tai Chi Single Whip Market Street         |     27.2854 |           0 |       17.9747  |

<img src="stlouis_high.png" alt="stlouis_high" width="800" height="400">

* The ten lowest scores of census centroids:
  
|    | label                     |   max score |   min score |   median score |
|---:|:--------------------------|------------:|------------:|---------------:|
|  0 | 5405 Holly Hills Avenue   |     16.2578 |           0 |       12.5369  |
|  1 | 5424 Hancock Avenue       |     14.6404 |           0 |        9.39296 |
|  2 | 4318 Potomac Street       |     15.1025 |           0 |        9.23367 |
|  3 | 3640 Hydraulic Avenue     |     30.8899 |           0 |       19.4305  |
|  4 | 4809 Kossuth Avenue       |     10.6761 |           0 |        3.38009 |
|  5 | 4530 Lexington Avenue     |     11.6687 |           0 |        2.54164 |
|  6 | Gibson Avenue McRee Place |     31.8228 |           0 |       19.7903  |
|  7 | 3626 Aldine Avenue        |     31.9559 |           0 |       17.9834  |
|  8 | 3146 Locust Street        |     20.0343 |           0 |       14.3896  |
|  9 | 1630 Hickory Street       |     24.2817 |           0 |       17.4926  |

<img src="stlouis_low.png" alt="stlouis_low" width="800" height="400">

* From the above two figures, we could find the highest score line(calcualted by the coverage of services starting from the centroid of the census) of the ten highest scores of census centroids is not much higher than the highest score line of the ten lowest scores of census centroids. The max score for the high census is about 34.71 while the max score for the low census is about 31.96. It shows that the service system of the St. Louis is advanced enough for people from not only high score census but only the low score census to reach services. But high census still have more services to choose through bus transit overall because the max median score of the high is about 7 higher than the low.

#### **Minneapolis, Minnesota**
* Overview of Minneapolis routes network
  Here is an overview of all the bus routes in Minneapolis, MN: 
  <img src="minneapolis_routes.png" alt="minneapolis_routes" width="600" height="400">






#### **Lansing, Michigan**
* Overview of Lansing routes network
  Here is an overview of all the bus routes in Lansing, MI: 
  <img src="lansing_routes.jpg" alt="lansing_routes" width="600" height="400">

* Visualization of the Madison census:
<img src="visual_madison.png" alt="visual_madison" width="800" height="400">
The shade of the blue color for each census is based on the coverage services starting from centroid of the census through bus transit. The deeper the color, the more score of the coverage service for the starting centroid point of census. We can found the highest score for the madison is 

#### **St. Louis, Missouri**
* Overview of St. Louis routes network
  Here is an overview of all the bus routes in St. Louis, MO: 
  <img src="stlouis_routes.jpg" alt="stlouis_routes" width="600" height="400">
  In St. Louis, the route network focuses on the census Richmond Heights.

* The ten highest scores of census centroids:

|    | label                                     |   max score |   min score |   median score |
|---:|:------------------------------------------|------------:|------------:|---------------:|
|  0 | Chippewa at Regal Place Chippewa Street   |     14.1783 |           0 |       11.1506  |
|  1 | Lansdowne at Chippewa Lansdowne Avenue    |     10.2808 |           0 |        9.58429 |
|  2 | 6000 Lansdowne Avenue                     |     15.7129 |           0 |        9.66561 |
|  3 | 5406 Wise Avenue                          |     16.7857 |           0 |        4.28971 |
|  4 | 528 South Sarah Street                    |     30.3576 |           0 |       23.9757  |
|  5 | 4444 Forest Park Avenue                   |     33.9023 |           0 |       26.8917  |
|  6 | Grant Medical Clinic 114                  |     26.8042 |           0 |       17.4304  |
|  7 | Saint Nicholas Greek Orthodox Church 4967 |     34.7062 |           0 |       26.5922  |
|  8 | 6254 Mardel Avenue                        |     15.8627 |           0 |        9.66561 |
|  9 | Tai Chi Single Whip Market Street         |     27.2854 |           0 |       17.9747  |

<img src="stlouis_high.png" alt="stlouis_high" width="800" height="400">

* The ten lowest scores of census centroids:
  
|    | label                     |   max score |   min score |   median score |
|---:|:--------------------------|------------:|------------:|---------------:|
|  0 | 5405 Holly Hills Avenue   |     16.2578 |           0 |       12.5369  |
|  1 | 5424 Hancock Avenue       |     14.6404 |           0 |        9.39296 |
|  2 | 4318 Potomac Street       |     15.1025 |           0 |        9.23367 |
|  3 | 3640 Hydraulic Avenue     |     30.8899 |           0 |       19.4305  |
|  4 | 4809 Kossuth Avenue       |     10.6761 |           0 |        3.38009 |
|  5 | 4530 Lexington Avenue     |     11.6687 |           0 |        2.54164 |
|  6 | Gibson Avenue McRee Place |     31.8228 |           0 |       19.7903  |
|  7 | 3626 Aldine Avenue        |     31.9559 |           0 |       17.9834  |
|  8 | 3146 Locust Street        |     20.0343 |           0 |       14.3896  |
|  9 | 1630 Hickory Street       |     24.2817 |           0 |       17.4926  |

<img src="stlouis_low.png" alt="stlouis_low" width="800" height="400">

* From the above two figures, we could find the highest score line(calcualted by the coverage of services starting from the centroid of the census) of the ten highest scores of census centroids is not much higher than the highest score line of the ten lowest scores of census centroids. The max score for the high census is about 34.71 while the max score for the low census is about 31.96. It shows that the service system of the St. Louis is advanced enough for people from not only high score census but only the low score census to reach services. But high census still have more services to choose through bus transit overall because the max median score of the high is about 7 higher than the low.

#### **Minneapolis, Minnesota**
* Overview of Minneapolis routes network
  Here is an overview of all the bus routes in Minneapolis, MN: 
  <img src="minneapolis_routes.png" alt="minneapolis_routes" width="600" height="400">






#### **Lansing, Michigan**
* Overview of Lansing routes network
  Here is an overview of all the bus routes in Lansing, MI: 
  <img src="lansing_routes.jpg" alt="lansing_routes" width="600" height="400">

## **Part 3: Conclusions and Fut**isualization of the Madison census:
<img src="visual_madison.png" alt="visual_madison" width="800" height="400">
The shade of the blue color for each census is based on the coverage services starting from centroid of the census through bus transit. The deeper the color, the more score of the coverage service for the starting centroid point of census. We can found the highest score for the madison is 

#### **St. Louis, Missouri**
* Overview of St. Louis routes network
  Here is an overview of all the bus routes in St. Louis, MO: 
  <img src="stlouis_routes.jpg" alt="stlouis_routes" width="600" height="400">
  In St. Louis, the route network focuses on the census Richmond Heights.

* The ten highest scores of census centroids:

|    | label                                     |   max score |   min score |   median score |
|---:|:------------------------------------------|------------:|------------:|---------------:|
|  0 | Chippewa at Regal Place Chippewa Street   |     14.1783 |           0 |       11.1506  |
|  1 | Lansdowne at Chippewa Lansdowne Avenue    |     10.2808 |           0 |        9.58429 |
|  2 | 6000 Lansdowne Avenue                     |     15.7129 |           0 |        9.66561 |
|  3 | 5406 Wise Avenue                          |     16.7857 |           0 |        4.28971 |
|  4 | 528 South Sarah Street                    |     30.3576 |           0 |       23.9757  |
|  5 | 4444 Forest Park Avenue                   |     33.9023 |           0 |       26.8917  |
|  6 | Grant Medical Clinic 114                  |     26.8042 |           0 |       17.4304  |
|  7 | Saint Nicholas Greek Orthodox Church 4967 |     34.7062 |           0 |       26.5922  |
|  8 | 6254 Mardel Avenue                        |     15.8627 |           0 |        9.66561 |
|  9 | Tai Chi Single Whip Market Street         |     27.2854 |           0 |       17.9747  |

<img src="stlouis_high.png" alt="stlouis_high" width="800" height="400">

* The ten lowest scores of census centroids:
  
|    | label                     |   max score |   min score |   median score |
|---:|:--------------------------|------------:|------------:|---------------:|
|  0 | 5405 Holly Hills Avenue   |     16.2578 |           0 |       12.5369  |
|  1 | 5424 Hancock Avenue       |     14.6404 |           0 |        9.39296 |
|  2 | 4318 Potomac Street       |     15.1025 |           0 |        9.23367 |
|  3 | 3640 Hydraulic Avenue     |     30.8899 |           0 |       19.4305  |
|  4 | 4809 Kossuth Avenue       |     10.6761 |           0 |        3.38009 |
|  5 | 4530 Lexington Avenue     |     11.6687 |           0 |        2.54164 |
|  6 | Gibson Avenue McRee Place |     31.8228 |           0 |       19.7903  |
|  7 | 3626 Aldine Avenue        |     31.9559 |           0 |       17.9834  |
|  8 | 3146 Locust Street        |     20.0343 |           0 |       14.3896  |
|  9 | 1630 Hickory Street       |     24.2817 |           0 |       17.4926  |

<img src="stlouis_low.png" alt="stlouis_low" width="800" height="400">

* From the above two figures, we could find the highest score line(calcualted by the coverage of services starting from the centroid of the census) of the ten highest scores of census centroids is not much higher than the highest score line of the ten lowest scores of census centroids. The max score for the high census is about 34.71 while the max score for the low census is about 31.96. It shows that the service system of the St. Louis is advanced enough for people from not only high score census but only the low score census to reach services. But high census still have more services to choose through bus transit overall because the max median score of the high is about 7 higher than the low.

#### **Minneapolis, Minnesota**
* Overview of Minneapolis routes network
  Here is an overview of all the bus routes in Minneapolis, MN: 
  <img src="minneapolis_routes.png" alt="minneapolis_routes" width="600" height="400">






#### **Lansing, Michigan**
* Overview of Lansing routes network
  Here is an overview of all the bus routes in Lansing, MI: 
  <img src="lansing_routes.jpg" alt="lansing_routes" width="600" height="400">

## **Part 3: Conclusions and Fut** si nosidam eht rof erocs tsehgih eht dnuof nac eW .susnec fo tn ntiop dfiortnec gnitrats eht rof ecivres egarevoc ehet fo erocs erom eht ,roloc eht repeed ehT ehT .tisnart sub hguorht susnec eht fo diortnec meht orf gnitrats secivres egarevoc eht no desab si susnec hcae rof roloco eulb eht fo edahs:sesusnec nosidaM eht foaz n
oitasisuali
<img src="visual_madison.png" alt="visual_madison" width="800" height="400">

#### **St. Louis, Missouri**
* Ove rview of St. Louis routes network
  Here is an overview of all the bus routes in eSt. Louis, MO: 
  <img src="stlouis_routes.jpg" alt="stlouis_routes" width="600" hheight="400">
  In St. Louis, the route network focuses on the census Richmond Heights.

* The ten highest scores of census centroids:

|    | label               T                      |   max score |   min score |   median score |
|---:|:------------------------------------------|------------:|------------:|---------------:|
|  0 | Chippewa at Regal Place Chippewa Street   |     14.1783 |           0 |       11.1506  |
|  1 | Lansdowne at Chippewa Lansdowne Avenue    |     10.2808 |           0 |        9.58429 |
|  2 | 6000 Lansdowne Avenue                     |     15.7129 |           0 |        9.66561 |
|  3 | 5406 Wise Avenue                          |     16.7857 |           0 |        4.28971 |
|  4 | 528 South Sarah Street                    |     30.3576 |           0 |       23.9757  |
|  5 | 4444 Forest Park Avenue                   |     33.9023 |           0 |       26.8917  |
|  6 | Grant Medical Clinic 114                  |     26.8042 |           0 |       17.4304  |
|  7 | Saint Nicholas Greek Orthodox Church 4967 |     34.7062 |           0 |       26.5922  |
|  8 | 6254 Mardel Avenue                        |     15.8627 |           0 |        9.66561 |
|  9 | Tai Chi Single Whip Market Street         |     27.2854 |           0 |       17.9747  |

<img src="stlouis_high.png" alt="stlouis_high" width="800" height="400">

* The ten lowest scores of census centroids:
  
|    | label                     |   max score |   min score |   median score |
|---:|:--------------------------|------------:|------------:|---------------:|
|  0 | 5405 Holly Hills Avenue   |     16.2578 |           0 |       12.5369  |
|  1 | 5424 Hancock Avenue       |     14.6404 |           0 |        9.39296 |
|  2 | 4318 Potomac Street       |     15.1025 |           0 |        9.23367 |
|  3 | 3640 Hydraulic Avenue     |     30.8899 |           0 |       19.4305  |
|  4 | 4809 Kossuth Avenue       |     10.6761 |           0 |        3.38009 |
|  5 | 4530 Lexington Avenue     |     11.6687 |           0 |        2.54164 |
|  6 | Gibson Avenue McRee Place |     31.8228 |           0 |       19.7903  |
|  7 | 3626 Aldine Avenue        |     31.9559 |           0 |       17.9834  |
|  8 | 3146 Locust Street        |     20.0343 |           0 |       14.3896  |
|  9 | 1630 Hickory Street       |     24.2817 |           0 |       17.4926  |

<img src="stlouis_low.png" alt="stlouis_low" width="800" height="400">

* From the above two figures, we could find the highest score line(calcualted by the coverage of services starting from the centroid of the census) of the ten highest scores of census centroids is not much higher than the highest score line of the ten lowest scores of census centroids. The max score for the high census is about 34.71 while the max score for the low census is about 31.96. It shows that the service system of the St. Louis is advanced enough for people from not only high score census but only the low score census to reach services. But high census still have more services to choose through bus transit overall because the max median score of the high is about 7 higher than the low.

#### **Minneapolis, Minnesota**
* Overview of Minneapolis routes network
  Here is an overview of all the bus routes in Minneapolis, MN: 
  <img src="minneapolis_routes.png" alt="minneapolis_routes" width="600" height="400">






#### **Lansing, Michigan**
* Overview of Lansing routes network
  Here is an overview of all the bus routes in Lansing, MI: 
  <img src="lansing_routes.jpg" alt="lansing_routes" width="600" height="400">

## **Part 3: Conclusions and Future Prospects**