import re
import pandas as pd

large_text = '''Name 1. ____________ is care given by specialists to help restore or improve function after an illness or injury.
(A)   Subacute care
(B)   Acute care
(C)   Adult day services
(D)   Rehabilitation
2.    Which of the following factors helps explain the purpose of and need for home health care?
(A)   Hospitals discharge patients after a longer period of time than they used to.
(B)   There are shrinking numbers of older and chronically ill people.
(C)   Family members are more able to care for aging relatives at home than in the past.
(D)   People who are ill or disabled feel more comfortable at home.
3.    What may be different about working in a home than working in a facility?
(A)   Personal care aides do not have a supervisor.
(B)   All clients' homes are set up the same way.
(C)   Personal care aides have more contact with the client's family.
(D)   Personal care aides do not need to communicate with others.
4.    Which of the following statements is true of clients?
(A)   Clients cannot make their own decisions.
(B)   Clients are not care team members.
(C)   Clients should not try to make choices about the care they want to receive.
(D)   The care team revolves around the client and his or her condition, treatment, and  progress.
5.    Which of the following statements is true of a personal care aide's responsibilities if an activity is not listed in the care plan?
(A)   The PCA should not perform the activity if it is•not listed on the care pJa·n.
(B)   The PCA should perform the activity if he or she believes it is best for the client.
(C)   The PCA should only perform the activity if the client says he wants it performed.
(D)   The PCA should consult other PCAs to see if they would perform the activity.
6.    What is one reason why reporting a client's changes and problems to the supervisor is a very important role of the person care aide?
(A)   The care plan must be updated as the client's condition changes.
(B)   Reporting changes is not a task that the PCA performs.
(C)   Depending on the client's changes, the PCA can decide if she wants to work that day or not.
(D)   The PCA can decide what medication  to prescribe for the client's current condition.
7.    Which of the following is a typical task that a PCA performs?
(A)   Changing a sterile dressing on an open wound
(B)   Giving skin care
(C)   Administering medication
(D)   Prescribing treatments
8.    Which of the following tasks is considered outside the scope of practice for a PCA?
(A)   Giving a client a bath
(B)   Inserting a tube into a client's body
(C)   Helping a client eat dinner
(D)   Transferring a client from the bed to a chair"
"Name:                                                                      Date                                   _
9.Which of the following statements is an example of a common  policy at a home health agency?
(A)   PCAs must follow the client's care plan.
(B)   PCAs should discuss personal problems with clients to keep them aware of what is happening in their lives.
(C)   PCAs are not responsible for completing paperwork.
(D)   PCAs should expect to receive gifts from clients if they are doing their job properly.
l 0.  A professional  relationship between an PCA and a client includes
(A)   Telling the client about problems with the supervisor
(B)   Calling the client Sweetie
(C)   Letting a client know if the PCA is in a bad mood
(D)   Keeping client information confidential
11.  A client has purchased a special gift for his PCA. What would be the best response by the PCA?
(A)   The PCA should refuse the gift but thank the client for thinking of her.
(B)   The PCA should accept the gift because she is unsure about her agency's policy on gifts.
(C)   The PCA should accept the gift and ask the client to keep it confidential.
(D)   The PCA should refuse the gift and tell the client that her employer is very unfair about employees accepting gifts from clients.
12.  What does the term empathy mean?
(A)   Empathy means being alert.
(B)   Empathy means being able to document honestly.
(C)   Empathy  means being able to identify with the feelings of others.
(D)   Empathy means taking responsibility for one's own actions.
13. The most important member of the care team is
(A)   The nurse
(B)   The personal care aide
(C)   The physician
(D)   The client
14.  What are two categories of clients who commonly need home care?
(A)   Clients who receive Medicaid assistance and clients who do not have health insurance
(B)   Clients who have a specific injury or illness and clients who need support in their home due to aging or other reasons
(C)   Clients who need babysitting for young children and clients who are healthy
(D)   Clients who are too busy to run errands and clients who are young I 5. Which of the following is a physical need?
(A)   The need for social interaction
(B)   The need for water  .
(C)   The need for self-esteem
(D)   The need for independence
16.  Which of the following is an example of a psychosocial  need?
(A)   The need for food
(B)   The need for sleep
(C)   The need for activity
(D)   The need for acceptance (E)
17.  If a PCA encounters a consenting adult client in a sexual situation, she should.
(A)   Provide privacy and leave the room.
(B)   Tell him that what he is doing is wrong.
(C)   Ask him to stop what he is doing.
(D)   Discuss it with the client's family."
"Name:                                                                       Date                                    _
18.  Which of the following statements is true of spiritual needs?
(A)   Clients will believe in God.
(B)   Clients will be Christians.
(C)   Clients will have different spiritual needs and beliefs.
(D)   Clients will not believe in God or a higher power.
19. If a PCA feels as if he cannot help a client with a problem, which of the following would  be the best response by the PCA?
(A)   ""You should talk to your pastor about that.""
(B)   ""I wish I could help you, but it's not my responsibility.""
(C)   ""You should try to be more positive.""
(D)   ""Let me ask my supervisor to call you.""
20.  Which of the following is an example of nonverbal communication?
(A)   Asking for a cookie
(B)   Pointing to a cookie    .
(C)   Writing a note requesting a cookie
(D)   Shouting for a cookie
21. An example of active listening is
(A)   PCA looking around the room while the client is speaking.
(B)   PCA finishing the client's sentences to make communication faster.
(C)   PCA focusing on the client and providing feedback.
(D)   PCA talking constantly so that there are no pauses in the conversation.
22.  Which of the following sentences is an example of a fact?
(A)   Mr. Craig needs a haircut.
(B)   Mr. Craig needed help to get to the bathroom today.
(C)   Mr. Craig is lonely.
(D)   Mr. Craig needs visitors.
23. If a client makes a request that a PCA cannot honor, what would be the best response by the PCA?
(A)   The PCA should ignore the request and hope that the client will not ask again.
(B)   The PCA should explain why the request cannot be fulfilled and report to her supervisor.
(C)   The PCA should call the client's doctor and ask if she can perform the request.
(D)   The PCA should honor the request but let the client know that she cannot do it again.
24. Which of the following should a PCA report about a client to her supervisor immediately?
(A)   Famjly fighting
(B)   Chest pain, high fever
(C)   Watching too much TV
(D)   Acting lonely
25.  Which of the following senses is not used in making observations?
(A)   Sight
(B)   Touch
(C)   Smell
(D)   Taste
26. Accurate documentation  is important because?
(A)   The medical chart includes information about the client's meal choices each day
(B)   Documentation  provides an up-to-date record of the client's status and care
(C)   Family members make copies of clients' medical charts
(D)   Personal care aides put their diagnoses in medical charts"
"Name:                                                              _
27.  When should documentation  be recorded?
(A)   Immediately after care is given
(B)   The next day
(C)   Whenever there is time
(D)   Before the care is given"
"Name 28. Which of the following occurrences is considered an incident and requires a report to be completed?
(A)   A family member who helps care for the client arrives late.
(B)   The client requests a food item that is not included in his special diet.
(C)   The client falls.
(D)   The client shows signs of improvement.
29.  Positive responses to cultural diversity include.
(A)   Valuing and respecting each person as an individual.
(B)   Seeing all people from a certain culture as being the same
(C)   Preferring people of one culture over those of other cultures
(D)   Making assumptions about a person based on stereotypes about their culture.
30.  If a client makes an inappropriate request of a PCA, the PCA should
(A)   Let the client know that favors cost more.
(B)   Call the client's children to inform them.
(C)   Politely let the client know that it is not allowed.
(D)   Tell the client that the PCA will quit if she is asked that again.
31.  For personal care aides, confidentiality means.
(A)   Not telling the supervisor about possible abuse of a client
(B)   Keeping client information private
(C)   Not documenting client problems
(D)   Sharing client information with the PCA's family
32.  With whom may a PCA share a client's medical infonnation?
(A)   With the client's brother and sister
(B)   With the PCA 's  parents
(C)   With other members of the care team
(D)   With the client's children
33.  Which of the following statements is true of the normal aging process?
(A)   Most elderly people are entirely dependent on others.
(B)   Most elderly people are disabled and cannot walk.
(C)   Most elderly people are active and engaged  in activities.
(D)   Most elderly people cannot manage their own money.
34.  One way a PCA can help with normal changes of aging related to the integumentacy system is to
(A)   Withhold fluids so the client will not have to use the toilet often.
(B)   Layer clothing and bed covers for warmth.
(C)   Shampoo hair at least once a day.
(D)   Bathe elderly clients twice a day
35.  To prevent or slow osteoporosis, clients should?
(A)   Be discouraged from doing any form of exercise.
(B)   Be encouraged  to do light exercise.
(C)   Sit most of the time to avoid falls.
(D)   Have the PCA do everything for the client."
"Name:                                                                      Date                                   _
36.  For clients who are hearing-impaired, the PCA should
(A)   Speak slowly and clearly in good lighting.
(B)   Keep her hands in front of her face.
(C)   Speak loudly or shout.
(D)   Turn away from the client when speaking.
37. One way a PCA can help with normal changes of aging related to the urinary system is to
(A)   Offer frequent trips to the bathroom.
(B)   Withhold fluids.
(C)   Scold clients who are incontinent
(D)   Make sure every client wear incontinence briefs
38.  Which of the following statements is true of older adults and psychological changes?
(A)   Depression is a normal sign of aging.
(B)   Dementia is a normal sign of aging.
(C)   Disorientation is a normal sign of aging.
(D)   Some forgetfulness  is a normal sign of aging.
39.  Which of the following is a function of the circulatory system?
(A)   Senses and interprets information  from the environment.
(B)   Supplies food, oxygen, and hormones to cells
(C)   Controls and coordinates all body functions.
(D)   Allows humans to reproduce.
40. Respiration consists of
(A)   Intake and output
(B)   Inspiration and expiration
(C)   Taking in oxygen and removing carbon dioxide
(D)   Dilation and contraction
4 I.  Which is one major function of the gastrointestinal system?
(A)   Maintains water balance in the body
(B)   Creates new human life
(C)   Protects the body against disease
(D)   Eliminates solid wastes from the body
42. The ability to think logically and clearly is called.
(A)   Cognition
(B)   Dementia
(C)   Awareness
(D)   Dysphagia
43.  When a client with AD shows memory loss, the PCA should
(A)   Repeat herself using the same words.
(B)   Tell the client that she already answered that question.
(C)   Remind the client every time she forgets something.
(D)   Give the client a long list of instructions to go over.
44.  If a client with AD has lost most of his verbal skills, the PCA should.
(A)   Assume the client cannot understand what is being said.
(B)   Use touch, smiles, and laughter.
(C)   Ask the client questions.
(D)   Not involve client in activities because it will only frustrate him"
"Name:                                                                       Date                                   _
45.  A PCA can respond to sundowning by
(A)   Adding more caffeine to the client's diet
(B)   Setting a bedtime routine and keeping it
(C)   Restricting exercise during the day
(D)  Scheduling activities during this time
46.  Development  in children from 6 to 12 years old centers on cognitive development. Cognitive development  means
(A)   Developing touching and feeling skills
(B)   Leaming right from wrong
(C)   Developing thinking and learning skills
(D)   Developing social relationship skills
47.  Eating disorders that adolescents may develop include
(A)   Trauma and injury
(B)   Viral and bacterial infections
(C)   Pregnancy and binging
(D)   Anorexia and bulimia
48.  Which of the following statements is true of children?
(A)   Children need nutritious food and fluids.
(B)   Children with disabilities do not have the same physical needs as other children.
(C)   Children do not need constructive discipline.
(D)   Children need less structure and routine than adults.
49.  Which of the following is a type of mistreatment that refers to not providing adequate food, clothing, or support to a child?
(A)   Neglect
(B)   Emotional abuse
(C)   Physical abuse
(D)   Sexual abuse
50. Children in their                           years develop vocabulary/language skills, learn to play cooperatively in groups, and begin to learn right from wrong.
(A)   School-age (ages 6 to 12)
(B)   Toddler (ages  I  to 3)
(C)   Adolescent (ages 13 to 19)
(D)   Preschool (ages 3 to 6)
51.  Which of the following stages of child development involves children learning to speak, gaining coordination of their limbs, and gaining control over their bladders and bowels?
(A)   Preschool (ages 3 to 6)
(B)   Toddler (ages 1 to 3)
(C)   Infancy (birth to 12 months)
(D)   Preadolescence (ages 10 to 13)
52.  Which of the following are emotional  needs that children have?
(A)   Nutritious foods and fluids
(B)   Love and affection and constructive discipline.
(C)   Fresh air and plenty of sleep
(D)   Regular exercise and time outdoors"
"Name:                                                                       Date                                    _
53.  Which of the following is an important factor that influences how a child responds to stress?
(A)   The child's intelligence level
(B)   The child's sense of humor
(C)   The cause of the stress and its frequency
(D)   The height and weight of the child
54.  Which of the following statements about children with disabilities is true?
(A)   Children with disabilities do not have the same emotional needs as other children.
(B)   Children with disabilities need less social contact with other children.
(C)   Children with disabilities should be treated as people with disabilities first, and as children second.
(D)   Children with disabilities have the same need for love and acceptance, encouragement, and guidance as other children.
55. Some key factors in working with parents/caregivers and families include which of the following?
(A)   Understanding family dynamics and roles within the family
(B)   Finding out personal information about family members before working with them
(C)   Being able to give advice to parents about parenting.
(D)   Being able to show children how to change the behavior of their parents.
56. Which of the following is a sign or symptom of mental  illness?
(A)   Adapting to change
(B)   Getting along with others
(C)   Controlling impulses
(D)   Being agitated
57. Mental illness can be made worse by
(A)   Eating a diet heavy in red meat and other animal-based  proteins
(B)   A strong sense of self-respect
(C)   Taking prescribed medications
(D)   Substance abuse
58. Which of the following statements is true about mental illness?
(A)   People with mental illness can control their symptoms.
(B)   Mental illness is a disease like any physical  illness.
(C)   Mentally healthy persons are unable to control their emotions.
(D)   Mental illness rarely disrupts a person's ability to function.
59.  A person who is mentally healthy
(A)   Can control and fulfill impulses appropriately.
(B)   Is unlikely to have relationships with others.
(C)   Cannot deal with stress well.
(D)   Does not take responsibility for decisions.
60. Signs and symptoms of clinical depression include.
(A)   Apathy
(B)   Intense hunger
(C)   Sudden chest pain
(D)   Fruity smelling breath
61. An intense, irrational fear of an object, place, or situation is a
(A)   Phobia
(B)   Coping mechanism
(C)   Fallacy
(D)   Situation response"
"Name:    .                                                                  Date                                         
62.  Which of the following is a good idea for a PCA who is caring for a client who is mentally ill?
(A)   The PCA should do everything for the client.
(B)   The PCA should administer the client's medication.
(C)   The PCA should support the client and his or her family and friends.
(D)   The PCA should encourage the client to-stop being mentally ill and just get better.
63.  Which of the following statements about observing mentally ill clients is true?
(A)   A PCA does not need to report a comment about suicide as long as it is a joke.
(B)   A PCA needs to report changes in mood.
(C)   Withdrawal does not need to be reported.
(D)   Imagined  physical symptoms do not need to be reported.
64.  A client has been acting a little strangely lately. She says that she cannot find money that she knows should  be in the house. She forgets simple things and seems irritable most of the time. Sometimes her PCA smells alcohol and cigarettes on her clothes when she is doing the laundry. What would be the best response by the PCA?
(A)   Call a counselor and suggest he come to the house to talk with the client.
(B)   Tell the client that that the PCA has noticed these issues and feels that the client has a problem.
(C)   Discuss what the PCA has noticed with the client's family in the hope of staging an intervention.
(D)   Report the PCA's observations to her supervisor.
65.  A brain disorder that affects a person's ability to think clearly and understand  reality is
(A)   Clinical depression
(B)   Claustrophobia
(C)   Generalized anxiety disorder.
(D)   Schizophrenia
66. An anxiety disorder that is characterized  by chronic anxiety and worry, even when there is no reason for concern is
(A)   Generalized anxiety disorder.
(B)   Posttraumatic stress disorder
(C)   Obsessive-compulsive disorder
(D)   Major depressive disorder
67.  Which of the following is a common set of treatments for mental illness?
(A)   Electroconvulsive (shock) therapy and psychosurgery
(B)   Medication and psychotherapy
(C)   Cognitive behavioral therapy and psychosurgery
(D)   Medication and electroconvulsive (shock) therapy
68.  Which of the following is true of developmental  disabilities?
(A)   Developmental disabilities are temporary.
(B)   Developmental  disabilities restrict physical and/or mental ability.
(C)   Developmental  disabilities are a fonn of mental illness.
(D)   People with developmental disabilities can never live or work independently.
69. Care of clients who are intellectually disabled includes which of the following goals?
(A)   Helping clients to recover from their disability
(B)   Making tasks as complicated as possible to promote cognitive skills
(C)   Discouraging social interaction so clients won't be embarrassed
(D)   Promoting clients' independence
70. Which of the following are disabilities that are present at birth or emerge during childhood?
(A)   Language disabilities
(B)   Developmental  disabilities
(C)   Emotional disabilities
(D)   Social disabilities"
"Name·:                                                                     Date                                   _
71.  Which of the following are types of developmental  disabilities?
(A)   Intellectual disabilities, Down syndrome, cerebral palsy, spina bifida
(B)   Amyotrophic lateral sclerosis, multiple sclerosis, Parkinson's disease
(C)   Hearing impairment, paresis (paralysis), vision impairment, glaucoma
(D)   Hypertension, cancer, cataracts
72.  A condition in which the person has suffered  brain damage either while in the uterus or during birth and which causes problems with muscle coordination, gait, and speech is
(A)   Cerebral palsy
(B)   Spina bifida
(C)   Down syndrome
(D)   Autism spectrum disorder
73.                                    occurs when part of the backbone is not well-developed at birth.
(A)   Cerebral palsy
(B)   Spina bifida
(C)   Down syndrome
(D)   Autism spectrum disorder
74.  Which of the following is helpful when caring for a person who has an intellectual disability?
(A)   Promote independence and encourage social interaction
(B)   Try to do everything for the person whenever possible
(C)   Do not repeat words more than once
(D)   Discourage teaching ADLs, as the person will not be able to understand  them
75.  How can a PCA help teach activities of daily living (ADLs) to clients with intellectual disabilities?
(A)   It is not possible for clients to perform ADLs on their own.
(B)   By breaking tasks into smaller steps
(C)   By writing the steps down on a piece of paper that clients can keep
(D)   By doing everything for clients
76.  Which of the following statements is true of autism spectrum disorder?
(A)   Surgery is the first course of treatment for autism.
(B)   When it is detected early, the chances of curing it are greater.
(C)   Children normally outgrow it.
(D)   Boys are more often affected than girls.
77.  Which of the following is a sign or symptom of autism spectrum disorder?
(A)   A part of the backbone may bulge out of the person's back.
(B)   The person has poor balance or posture and difficulty using the arms and hands.
(C)   The person has repetitive body movements and lacks the ability to empathize with others.
(D)   The person's hand muscles are impaired, and the legs are weak or stiff.
78.  Which of the following is a guideline to use when communicating with clients who have cerebral  palsy?
(A)   Avoid using touch as a form of communication.
(B)   Allow the client to move slowly.
(C)   If the client cannot speak, avoid talking to the client.
(D)   Encourage the client to be as dependent as possible to conserve energy."
"Name:                                                                       Date                                   _
79.  People with physical disabilities have the same social and emotional  needs that all humans have. These basic psychosocial needs include which of the following?
(A)   The need to be free from pain
(B)   The need for fluids
(C)   The need to have enough sleep.
(D)   The need to have a sense of worth.
80.  Which of the following is the most essential nutrient for life?
(A)   Vegetables
(B)   Water
(C)   Grains
(D)   Protein
81.  According to the USDA's MyPlate icon, which food groups should make up at least half of a person's plate?
(A)   Grains and proteins
(B)   Vegetables and fruits
(C)   Dairy and proteins
(D)   Grains and fruits
82.  Which of the following foods supplies the most calcium?
(A)   Grains
(B)   Nuts
(C)   Yogurt
(D)   Ground beef.
83.  According to MyPlate, what percentage of milk fat should  be in a person's dairy choices?
(A)   1%
(B)   2%
(C)   3%
(D)   4%
84. The condition that occurs when a person does not have enough fluid in the body is called
(A)   Fluid balance
(B)   Edema
(C)   Dehydration
(D)   Aspiration
85.  Which of the following is an effective way for a PCA to help prevent dehydration?
(A)   The PCA should encourage clients to drink every time she sees them.
(B)   The PCA should insist that clients drink juice because it is healthy.
(C)   The PCA should withhold fluids if clients are incontinent.
(D)   The PCA should start an IV line for clients who are dehydrated.
86.                    is taking in and eliminating equal amounts of fluid.
(A)   Dehydration
(B)   Input
(C)   Fluid balance
(D)   Restrict fluids
87. At a minimum, how many ounces of water or other fluids should clients be encouraged to drink each day?
(A)   110 ounces
(B)   28 ounces
(C)   96 ounces
(D)   64 ounces"
"Name:                                                                      Date --------
88.  What does the abbreviation NPO mean?
(A)   Nothing pureed only
(B)   Not prepared on-site
(C)   Nothing by mouth
(D)   Note preferences only
89.  How should clients be positioned for eating?
(A)   On their sides
(B)   Sitting upright
(C)   Flat on their backs
(D)   On their stomachs
90.  A diet that consists of foods that are chopped to help people who have trouble chewing and swallowing is called a
(A)   Low-cholesterol diet
(B)   High-potassium diet
(C)   Low-residue diet
(D)   Soft diet
91. Generally speaking, which types of food are best to buy for the client?
(A)   Ready-made foods
(B)   Processed foods
(C)   Fresh foods
(D)   Already-mixed  foods
92.  What is a good way for a PCA to help prevent foodbome illness?
(A)   Use the same cutting board for meat as she does for vegetables.
(B)   Leave meats sitting on the counter to defrost them.
(C)   Use cold water to wash utensils.
(b)   Put warm foods in the refrigerator before they cool.
93.  What does the phrase; ""When in doubt, throw it out,"" mean?
(A)   Old clothes should be discarded if not worn.
(B)   Old food should  be discarded if there is a chance of spoilage.
(C)   Expired medication should  be discarded.
(D)   Meal plans should be discarded if the client is not interested  in them.
94.  How can a PCA best help clients with eating?
(A)   The PCA should do everything for clients during mealtime so clients will not be anxious.
(B)   The PCA should choose which foods clients eat first.
(C)   The PCA should chat with friends while clients are eating since clients will be busy.
(D)   The PCA should sit and talk with clients while they eat.
95.  Which of the following statements is true of helping to prevent aspiration?
(A)   The PCA should  place food in the non-paralyzed side of the mouth.
(B)   The PCA should offer big pieces of food.
(C)   The PCA should position the client on his back to help him eat.
(D)   The PCA should feed the client quickly.
96.  Which of the following is a symptom of dysphagia (difficulty swallowing)?
(A)   Coughing during meals
(B)   Talking during meals
(C)   Laughing during meals
(D)   Drinking during meals"
"Name:                                                                Date                                 _
97. Which type of clients may have an order for thickened liquids?
(A)  Clients who refuse to drink water
(B)   Clients who do not eat meat
(C)   Clients who have swallowing problems
(D) . Clients who have certain religious beliefs
98. This type of diet limits intake of egg yolks and fried foods and is used for people who are at risk for heart attacks and heart disease.
(A)  Low-sodium diet
(B)   Low-protein diet
(C)   Low-residue diet
(D)   Low-cholesterol diet
99.  Which of the following is one way that clients who have diabetes eat a healthy diet?
(A)   By counting carbohydrates (carb-counting)
(B)   By eating whatever they want but keeping track of it in a food diary
(C)   By adding more sugar into their diet
(D)  By eating large amounts of food and then exercising vigorously to bum calories
100.      This type of diet increases the intake of fiber and whole grains and is prescribed for clients who have constipation and bowel disorders.
(A)  High-residue diet
(B)   Liquid diet
(C)   Gluten-free diet
(D)   Low-cholesterol diet
101.      To                               means to blend or grind food into a thick paste that matches the consistency of baby food.
(A)   Liquefy
(B)   Puree
(C)   Pummel
(D)  Smooth
102.      Which of the following is a good money-saving tip?
(A)  Plan ahead to get what you need before you run out.
(B)   Shop at convenience stores for groceries.
(C)   Buy prepared foods rather than fresh or raw foods.
(D)   Buy whatever sounds good, even if it is not on the list.
103.      Which of the following is true of handling a client's money?
(A)   A PCA can borrow a client's money if she plans to pay it back.
(B)   All states allow PCAs to handle clients' money.
(C)   PCAs should use checks rather than cash, when possible.
(D)    The PCA should give money advice if she knows the client is struggling financially.
104.      Which of the following statements is true?
(A)   Prepared foods are less expensive than raw foods.
(8)   Checking store circulars for advertised specials is a good way to plan menus around foods that are a good value.
(C)   Seeing what catches your eye at the store rather than planning menus in advance saves money.
(D)   Buying fast food rather than cooking is often the best deal."
"Name:                                                            _     Date                                   _
105.      Which of the following is a good idea to take to the grocery store to help stay within a budget?
(A)   Receipt
(B)   Calculator
(C)   Wallet
(D)   Cash
106.      Which of the following can help clients save money when grocery shopping?
(A)   Checkbook
(B)   Piggy bank
(C)   Coupons
(D)   Convenience store
107.      What is important for PCAs to give to clients after making purchases for them?
(A)   Coupon
(B)   Store voucher.
(C)   Cancelled check.
(D)   Receipt
I 08.      Where should a PCA keep a client's cash?
(A)   In the PCA's wallet
(B)   In the PCA's safe
(C)   Separate from the PCA's money.
(D)   In the PCA's coin purse
109.      Which of the following statements is true of a client's financial  information?
(A)   The PCA should not discuss the client's information with anyone.
(B)   The PCA should discuss any purchases the client makes with his children.
(C)   The PCA should offer financial advice if the client seems to need it.
(D)   The PCA should discuss any financial concerns with the client's bank representative.
110.      When should PCAs return receipts to clients?
(A)   At the end of the day
(B)   At the beginning of the next shift
(C)   Immediately
(D)   When the client inquiries about it
I I I.       Forgetting to return change could be viewed by the client or a family member as
(A)   Carelessness
(B)   Emotional abuse
(C)   Forgetfulness
(D)   Stealing
I 12.      What kind of housekeeping assignments can PCAs expect to receive?
(A)   Cleaning out the garage
(B)   Dusting and vacuuming
(C)   Mowing the lawn
(D)   Washing windows
I 13.      Which of the following is a quality needed to effectively care for a client's home?
(A)   Sense of humor
(B)   Sensitivity
(C)   Curiosity
(D)   Creativity"
"Name:                                                             _     Date                                   _
114.      Which of the following products should never be mixed together?
(A)   Bleach and ammonia.
(B)   Water and vinegar
(C)   Mild soap and water
(0)    Baking soda and salt
115.      Which of the following is considered a basic cleaning tool?
(A)   Laundry soap
(B)   Automatic dishwasher
(C)   Vacuum cleaner
(0)    Lawn mower
116.      How often should garbage in the kitchen be disposed of?
(A)   Weekly
(B)   Monthly
(C)   Bi-weekly
(0)    Daily
117.      When washing dishes for a client who has an infectious disease, the PCA should add               to the soapy water.
(A)   Peroxide
(B)   Bleach
(C)   Vinegar
(0)    Scouring powder
118.      Which of the following statements is true of the refrigerator?
(A)   It should be cleaned once a week.
(B)   It should be cleaned every day.
(C)   It should be cleaned once a month.
(0)    It should be cleaned twice a year.
119.      How should a PCA clean the bathroom?
(A)   From dirtiest to cleanest
(B)   From front to back
(C)   From top shelves down
(D)   From cleanest to dirtiest
120.      A common household item that can be used to clean surfaces and eliminate odors is
(A)   Flour
(B)   Salt
(C)   Baking soda
(D)   Sugar
121.      When a client has a known infectious disease, the PCA should.
(A)   Use cold water when washing dishes.
(B)   Use separate dishes and utensils for tqe client.
(C)   Dry dishes with towels
(0)    Clean kitchen surfaces with plain water
122.      Which of the following is true of handling laundry for a client with an infectious disease?
(A)   The PCA should carry laundry close to her body when taking it to the laundry room.
(B)   The PCA should shake the laundry first to get rid of dirt before taking it to be washed.
(C)   The PCA should combine the client's laundry with other family members' laundry.
(D)   The PCA should wear gloves when handling the laundry."
"Name:                                                            _     Date --------
123.      In which type of environments do microorganisms thrive?
(A)   Cool, dry environments
(B)   Clean, cold environments
(C)   Dry, hot environments
(D)   Warm, moist environments
124.      How often should sheets be changed?
(A)   When they are soiled, wrinkled, or damp
(B)   Every other day
(C)   Twice a week
(D)   Daily
125.      Which of the following tasks should  be given first priority?
(A)   Shopping for cosmetics
(B)   Giving the client a bath
(C)   Cleaning out the refrigerator
(D)   Preparing a cake for dinner
126.      Which of the following tasks should  be given first priority?
(A)   Assisting with oral care
(B)   Clipping coupons
(C)   Chopping vegetables
(D)   Cleaning the oven
127.      Which of the following tasks should be given first priority?
(A)   Picking up clutter
(B)   Running to the store
(C)   Giving a back massage
(D)   Dusting
128.      Why is housekeeping important to both physical and psychological  well-being?
(A)   Families who lack knowledge about managing their home cannot be taught these skills.
(B)   Clients feel better, and infections and accidents are more likely to be prevented.
(C)   Everyone prefers to have a tidy home.
(D)   Clients benefit more from a clean house than they do from having their medical needs addressed.
129.      Which of the following statements is true of body mechanics?
(A)   Body mechanics help save energy and prevent injury.
(B)   The narrower a person's base of support, the more stable the person is.
(C)   Proper alignment of the body means that the two sides of the body should not line up.
(D)   Twisting at the waist is the best way to maintain body alignment.
130.      When helping a client sit up, stand  up, or walk, the PCA should
(A)   Keep her feet together
(B)   Bend her upper body
(C)   Bend her knees
(D)   Try to catch the client if he starts to fall
I 31.      Which of the following is a way to use proper body mechanics?
(A)   The PCA should twist at the waist when lifting objects.
(B)   The PCA should stand with her legs shoulder-width apart.
(C)   The PCA should  lift, rather than push or slide objects.
(D)   The PCA should carry objects away from her body."
"Name:                                                                      Date                                   _
132.      Which of the following statements is true of preventing falls?
(A)   Clear walkways of clutter.
(B)   Keep lights low.
(C)   Leave spills for family members to clean.
(D)   Use wax on floors to make them easy to walk on.
133.      When serving hot drinks to clients, the PCA should
(A)   Pour hot drinks away from clients.
(B)   Place hot drinks on the edges of tables so that they will be easier to reach.
(C)   Take lids off of hot drinks just before serving.
(D)   Make sure clients are standing up before serving hot drinks.
134.      In which position should a client be placed while eating?
(A)   Lying flat on his back
•   (B)   Reclining at a 45-degree angle
(C)   Lying on his side with his arm propping his head up
(D)   Sitting as upright as possible
135.      If the PCA must leave something in his car when using the car for work, which of the following  is the best place to leave it?
(A)   On the driver's seat
(B)   In the trunk
(C)   On the passenger's seat
(D)   On the dashboard
136.       What should the PCA do if he reaches a client's home and finds nobody is there?
(A)   Let himself in and start housekeeping tasks
(B)   Call his supervisor and not enter the home.
(C)   Let himself in but wait to begin work until the client arrives.
(D)   Let himself in and start cooking lunch or dinner.
137.      Which of the following is information a PCA should be prepared to give when calling emergency services?
(A)   Her supervisor's name.
(B)   The phone number and address where the emergency is happening.
(C)   The correct diagnosis of the victim
(D)   The names of client's family members
138.      In which of the following situations should a PCA give abdominal thrusts to a client?
(A)   The client is coughing.
(B)   The client cannot speak, breathe, or cough.
(C)   The client is breathing very rapidly.
(D)   The client tells the PCA that she feels short of breath.
139.      When a client is suspected of having a heart attack, a PCA should
(A)   Loosen clothing around the neck.
(B)   Give the client some water.
(C)   Put medication directly into the client's mouth.
(D)   Wait and see if the episode subsides before calling emergency services."
"Name:                                                                       Date --------
140.      To control bleeding, a PCA should
(A)   Lower the wound below the heart.
(B)   Use a topical antibiotic cream on the wound.
(C)   Hold a thick pad against the wound and press down hard
(D)   Apply light pressure with a bandage.
141.       Which of the following should a PCA do if he suspects poisoning?
(A)   The PCA should offer an over-the-counter medicine to induce vomiting.
(B)   The PCA should don gloves and look for a container that will help determine what the client took or ate.
(C)   The PCA should feed the client crackers or bread to soak up the poison.
(D)   The PCA should give the client medication and then call the client's doctor.
142.      To treat a minor burn, a PCA should use                                 to decrease the temperature of the skin.
(A)   Ice or ice water.
(B)   Cool water
(C)   Ointment
(D)   Butter
143.      If a client faints, a PCA should.
(A)   Lower him to the floor.
(B)   Position him curled up in a ball.
(C)   Elevate his legs one inch.
(D)   Help him stand up immediately.
144.      In which rooms within the home do accidents and injuries occur most frequently?
(A)   Living room and bathroom
(B)   Kitchen and bathroom
(C)   Bedroom and kitchen
(D)   Dining room and family room
145.      Which of the following is an example of an·activity of daily living (AOL)?
(A)   Praying
(B)   Eating
(C)   Reading
(D)   Talking to a family member
146.      Which of the following statements is true of assisting clients with personal care?
(A)   All clients will want to use the same skin care products.
(B)   Clients' routines and preferenqes should be followed.
(C)   Clients with disabilities do not make choices about their personal care.
(D)   PCAs do not need to explain  personal care tasks to clients before beginning.
147.      One  way for an PCA to promote dignity and independence  with personal care is to
(A)   Encourage clients to perform tasks independently even if it takes longer
(B)   Choose which clothes clients will wear for the day
(C)   Encourage clients to bathe quickly
(D)   Leave clients alone while bathing
148.      Which of the following should  be washed every day?
(A)   Perineum
(B)   Hair
(C)   Chest
(D)   Knees"
"Name:                                                                      Date                                   _
149.      When bathing a client, an PCA should
(A)   Leave the client alone to promote self-care
(B)   Make sure the room is warm enough before beginning
(C)   Use bath oils to moisturize the client's skin
(D)  Talk with family members while helping the client bathe
150.      When cleaning the perinea! area, the PCA should
(A)   Work from front to back
(B)   Work from back to front
(C)   Work from side to side
(D)  Work from dirtiest area to cleanest area
151.      Which of the following is true of nail care?
(A)   An accidental cut when providing nail care poses no great risk.
(B)   An orangewood stick should  be used to smooth calluses and corns.
(C)   Nail care should be provided  when the nails are dirty.
(D)  A client's toenails should  be trimmed  by the PCA when they are long.
152.      How can an PCA help promote independence and dignity while assisting with grooming?
(A)   By doing things clients can do for themselves only when the PCA is in a hurry
(B)   By letting clients make choices once in a while
(C)   By styling the client's hair in cute new ways
(D)  By honoring the client's preferences
153.      During which of the following procedures must an PCA always wear gloves?
(A)   Shaving a client
(B)   Combing a client's hair
(C)   Dressing a client
(D)  Turning a client
154.      Which of the following statements is true of hair care?
(A)   Pediculosis (lice) cannot spread quickly.
(B)   Clients' hair should be combed or brushed into childish hairstyles because they are cute.
(C)   PCAs should cut clients' hair if it is getting long.
(D)  Clients' hair should be handled gently because hair can be pulled out when combing or brushing it.
155.      Which of the following is an appropriate way for an PCA to refer to a client's weakened side when assisting with dressing?
(A)   Bad side
(B)   Involved side  .
(C)   Stiff side
(D)   Limp side
156.      Which of the following is true of helping a client dress?
(A)   An PCA should choose the client's clothing for the day.
(B)   The client should do as much to dress himself as possible.
(C)   If a client has weakness on one side, the PCA should start with the stronger side when dressing.
(D)  Clients should dress in nightclothes during the day.
157.      Oral care should be done at least          time(s) a day.
(A)   One
(B)   Two
(C)   Three
(D)   Four"
"Name:                                                                      Date                                   _
158.      Ways to prevent aspiration during oral care of unconscious clients include
(A)   Using as little liquid as possible when giving oral care
(B)   Turning clients on their stomachs when giving oral care
(C)   Not giving frequent mouth care
(D)   Pouring water slowly into the client's mouth
159.      Clients who are unconscious may still be able to
(A)   Speak
(B)   Gesture
(C)   Hear
(D)   See
160.      Which of the following statements is true of dentures?
(A)   Dentures should  be cleaned with hot water to remove bacteria.
(B)   Clean dentures should be returned to the client or stored  in a denture cup.
(C)   Dentures are not expensive.
(D)   Wearing gloves is not required for cleaning dentures.
161.      Which of the following statements is true of hearing aids?
(A)   Hearing aids should  be wiped with a soft cloth and special cleaning solution.
(B)   Soaking hearing aids in water makes them easier to clean.
(C)   Hearing aids should remain on the ear while the person is in the shower.
(D)   Hearing aids should be left on when not in use to keep the battery charged.
162.      Which type of toileting equipment is used for elimination  when clients cannot assist with raising their hips very far in bed?
(A)   Urinal
(B)   Portable commode
(C)   Raised toilet seat
(D)   Fracture pan
163.      When assisting a client with a standard  bedpan, where should the wider end of the bedpan be placed?
(A)   Toward the foot of the bed
(B)   In alignment with the client's buttocks
(C)   Inside the portable commode
(D)   Toward the side of the bed where the PCA is standing
164.      How should a fracture pan be positioned?
(A)   With the handle toward the head of the bed
(B)   With the handle toward the foot of the bed
(C)   With the handle facing the side the PCA is standing on
(D)   With the handle facing the window
165.      Washcloths that were used to wash perineal areas should  be
(A)   Washed in cold water
(B)   Washed in hot water
(C)   Discarded
(D)   Rinsed with water only-no soap
166.      A client who is lying on either her left or her right side is in the                position.
(A)   Supine
(B)   Lateral
(C)   Prone
(D)   Fowler's"
"Name:                                                                      Date                                     _
167.      A client who has her head and shoulders elevated and is in a semi-sitting position (45 to 60 degrees) is in the position.
(A)   Sims'
(B)   Fowler's
(C)   Prone
(D)   Lateral
I 68.      A client who is lying on her stomach with her arms at her side is in the                   position.
(A)   Sims'
(B)   Fowler's
(C)   Prone
(D)   Lateral
169.      A client who is lying on her left side with her upper knee flexed and raised toward the chest is in the            _ position.
(A)   Sims'
(B)   Fowler's
(C)   Prone
(D)   Supine
170.      A client who is lying on her back with her head and shoulders supported  with a pillow is in the            _ position.
(A)   Sims'
(B)   Fowler's
(C)   Prone
(D)   Supine
171.      Which of the following means rubbing or friction that results when the skin moves one way and the bone underneath it remains fixed or moves in the opposite direction?
(A)   Turning sheet
(B)   Logrolling
(C)   Draw sheet
(D)   Shearing
172.      Dangling means
(A)   Sitting up with feet over side of bed
(B)   Sitting up in chair with feet on floor
(C)   Lying in bed with feet over side of bed
(D)   Hanging both arms over chair rests
173.      When using a transfer belt, the PCA should
(A)   Place it underneath the client's clothing
(B)   Place it around the client's shoulders
(C)   Place it around the client's chest
(D)   Place it over the client's clothing
174.      When transferring clients who have a strong side and a weak side, the PCA should plan the move so that
(A)   The stronger side moves first
(B)   The weaker side moves first
(C)   Both feet move at the same time
(D)   The wheelchair moves first"
"Name:                                                                      Date                                   _
175.      Which of the following is true of mechanical lifts?
(A)   Mechanical  lifts prevent wear and tear on the body.
(B)   It is safer for PCAs to lift clients without the use of a mechanical lift.
(C)   There is only one kind of mechanical lift.
(D)   When using a mechanical  lift, the PCA should  pump it approximately five feet over the bed before moving the client.
176.      If a client starts to fall, the best thing an PCA can do is to
(A)   Catch the client under the arms to stop the falt
(B)   Widen her stance and bring the client's body close to her
(C)   Lock her knees.
(D)   Move out of the way.
177.      Which of the following canes has four rubber-tipped feet?
(A)   Quad cane
(B)   Functional grip cane
(C)   C cane
(D)   Crutch cane
178.      When a client can walk, he or she is
(A)   Ambulating
(B)   Accessorizing
(C)   Abducting
(D)   Adducting
179.      Which of the following is a positioning device that helps prevent foot drop?
(A)   Handrail
(B)   Trochanter roll
(C)   Footboard
(D)   Backrest
180.      Another name for elastic stockings is
(A)   Elastic bandages
(B)   Dry dressings
(C)   Heel stockings.
(D)   Anti-embolic stockings
181.      The abbreviation J&O means
(A)   Input and oral
(B)   Intake and output
(C)   Insert and order
(D)   Input and off"
"Name:                                                                       Date                                         
184.      Apnea monitors are used for
(A)   Monitoring pain level
(B)   Monitoring body temperature
(C)   Monitoring breathing
(D)   Monitoring oxygen tanks"
"Name 185.      To  help prevent diaper rash
(A)   Keep the baby's bottom covered at all times
(B)   Keep the baby wet
(C)   Change the baby frequently
(D)   Use only plastic diapers
186.      Which of the following items should  be ready for use when giving a sponge bath to an infant?
(A)   Clean diaper
(B)   Baby thermometer
(C)   Baby wipe warmer
(D)   Talcum powder
187.      The  purpose of umbilical cord care is to
(A)   Prevent infection
(B)   Slow healing
(C)   Remove the cord early
(D)   Lubricate the area
188.      Which of the following is an over-the-counter drug?
(A)   Heart medication (such as nitroglycerin)
(B)   Acetaminophen (such as Tylenol)
(C)   Antibiotics (such as penicillin)
(D)   Pain medication (such as codeine)
189.      Which of the following is part of the five ""rights"" of medication?
(A)   Right Home Health Aide
(B)   Right Note
(C)   Right Report
(D)   Right Client
190.      Which of the following is a way PCAs may help clients with self-administered medications?
(A)   Mix medication with food or drink.
(B)   Take the medication  out of the bottle for the client.
(C)   Provide food or water to take with medication.
(D)   Place the medication  in the client's mouth.
191.      Which of the following is an PCA not allowed to do when assisting a client with medications?
(A)   Shake liquid medications.
(B)   Report possible reactions to the medication to the supervisor.
(C)   Cut tablets in half
(D)   Read the medication  label to the client.
192.      Which of the following statements is true?
(A)   Because prescription  drugs are legal, they cannot be abused.
(B)   There is nothing wrong with taking drugs that were prescribed for someone else as long as the person taking them has the same condition.
(C)   Misuse of prescription drugs can be fatal.
(D)   Medications work their best when taken with alcoholic beverages."
"Name:                                                                      Date --------
193.      An PCA discovers that a client has taken another household member's prescription  medication  by mistake. What
should the PCA do?
(A)   The PCA should give the client syrup of ipecac to induce vomiting.
(B)   The PCA should call the local poison control center immediately.
(C)   The PCA should encourage the client to eat carbohydrates to soak up the medication  in his stomach.
(D)   The PCA should wait to see if there is an adverse reaction, then call her supervisor.
194.      How should a baby be placed in a crib?
(A)   On his stomach
(B)   On his side
(C)   On his back
(D)   On a pillow
195.      Why does working with oxygen equipment require special safety precautions?
(A)   Oxygen equipment is very difficult to obtain.
(B)   Oxygen is a dangerous fire hazard.
(C)   Oxygen levels must be adjusted often.
(D)   Oxygen equipment  is very fragile.
196.      Which of the fol lowing statements is true of proper medication storage?
(A)   Medications should be stored away from heat and light.
(B)   The PCA is responsible for disposing of expired medications.
(C)   Medications can be disposed of in the trash.
(D)   Medications should  be stored on lower shelves in the refrigerator if children are in the house.
197.       How should the PCA respond  if a client refuses to take certain medications?
(A)   The PCA should insist that the client take the medication, telling the client it will cure his illness.
(B)   The PCA should call the client's family to see if they can get the client to take the medication.
(C)   The PCA should try to find out why the client does not want to take the medication  and report to the supervisor.
(D)   The PCA should explain that the PCA could lose her job  unless the medication  is taken.
198.   •  Which of the following is an example ofa  prosthesis?
(A)   An artificial eye to replace an eye that has been lost.
(B)   Handrolls to keep clients' fingers from curling too tightly.
(C)   Special shoes to help clients with flat feet.
(D)   Adaptive devices to assist clients with dressing.
199.      Orthotic devices are used to
(A)   Keep joints in correct position and improve function.
(B)   Assist clients with activities of daily living.
(C)   Maintain proper body alignment.
(D)   Prevent rubbing, irritation, and pressure injuries.
'''


# Regex to extract all 199 questions
all_questions = re.findall(r"\d+\.\s(.*?)(?=\n\(\w\)|\d+\.)", large_text, re.DOTALL)

# Create a DataFrame for all questions
df_all_questions = pd.DataFrame(all_questions, columns=["Question"])

# Save to CSV
all_questions_path = "C:\\Users\\nochu\\Downloads\\parsed_questions_fixed.csv"
df_all_questions.to_csv(all_questions_path, index=False)