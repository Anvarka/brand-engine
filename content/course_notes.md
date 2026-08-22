# Course notes

Auto-extracted from the lecture decks by scripts/course_extract.py.

Raw material for the recsys_101 pillar; each `##` section is one topic.


## Deep learning for recommender systems_ A Netflix case study

- slide 1: Deep learning for recommender systems: A Netflix case study | Tliamov Anvar
- slide 3: Рекомендательная система Netflix | Рекомендательная система – это множество разных алгоритмов рекомендации | В Netflix существуют алгоритмы для рекомендации просмотренного контента, нового и так далее | Метрика: retention | Такая комбинация моделей дает хороший diversity
- slide 4: Данные | Пользовательское взаимодействие можно представить двумя способами: | Explicit и Implicit | Explicit: явная оценка пользователя | Implicit: неявно пытаемся оценить предпочтение пользователя
- slide 5: Алгоритмы | Метрика | : увеличить вовлеченность пользователя | Алгоритм: | множество алгоритмов чтобы повысить разнообразие и не только | Без учета времени: | Bag of items | С учетом времени: | Sequence models
- slide 6: Hello everyone! Welcome to the Recommendation Systems course! | In this course, we’ll explore what recommendation systems are, why they matter, and how they are used in areas like e-commerce, streaming services, and social media. | We’ll mainly focus on the algorithms that make recommendation systems work. | This course includes lectures and summaries. | It’s best | to watch the lecture first, then read the summary. After that, you can answer the questions at the end of the module | to better understand the concepts | . | Let’s get started!
- slide 7: Bag of items: победители Netflix prize | Не учитывается информацию о времени | Собирает всю информацию о провзаимодейственных объектах в множество | Одни из победителей соревнования: RBM и виды матричной факторизации
- slide 8: RBM | Restricted Boltzmann Machine: один из призеров в соревновании Netflix prize | Пытается понять распределение данных и за счет этого делать рекомендации | Дает нестабильные рекомендаций, поэтому не совсем подходит для использования
- slide 9: Матричная факторизация | Строится матрица взаимодействия, которая раскладывается в виде произведения двух матриц | Исходная матрица разделяется на две матрицы | Первая матрица: матрица пользователей | Вторая матрица: матрица объектов
- slide 10: Связь моделей с Deep learning | RBM: использовали предобученные модели Deep Learnin | g | из CV | Matrix Factorization | : многие современные рекомендательные системы используют именно такую архитектуру | Matrix Factorization связан с Deep learning через | автоэнкодеры
- slide 11: AutoEncoder | Состоит из двух частей: | Encoder: input vector превращает в вектор меньшей размерности | Decoder: из вектора меньшей размерности пытается восстановить input vector | Output vector должен быть похож на input vector
- slide 12: Применение AutoEncoder | Matrix factorization: обычный алгоритм рекомендации | Asymmetric matrix factorization: | матричная факторизация через автоэнкодеры
- slide 13: Применение AutoEncoder: item2item | Давайте увеличим размерность внутреннего слоя до размерности входного | Тогда мы будем получать матрицу подобия item к item | Таким образом, будем решать проблему поиска похожих видео | Модели: | SLIM model, | EASE model
- slide 14: D | eep feedforward model | Можно уменьшить размерность выходного вектора | И обучаться так, чтобы предсказывались последние просмотренные видео | Тогда модель будет лучше будет понимать текущие предпочтения пользователя
- slide 15: Sequential models | Последовательность взаимодействий можно использовать как предложение | В дальнейшем, запустить | LSTM, GRU, BERT на них | Получим векторные представления | Explainabilty: | Инструменты: LIME, SHAP, Integrated Gradients
- slide 16: Время как фича | Попробовали по-разному добавить фичу времени. | Время как | дискретная величина: | Время используют как дискретную величину | То есть разбивка происходит по неделям, по дням | Время как непрерывная величина: | Рост на 30 процентов по сравнению с дискретным
- slide 17: Контентные фичи | можно использовать метаданные из видео | Для музыки, например, нужна модель обработки звука | Данные контентные фичи улучшают качество рекомендации | Однако необходимо учить дополнительную модель
- slide 18: Корреляция оффлайн и онлайн метрик | Часто смотрим на количество кликов и лайков | Хотим же по факту улучшить долгосрочную удовлетворенность пользователя | Цель: нужны способы обучения на short-term поведении, которые бы оптимизировали long-term | Также есть проблема шума short-term данных
- slide 19: Заключение | Существуют алгоритмы с учетом времени и без | Без учета: используют матричную факторизацию(MF) | MF можно написать через автоэнкодеры | С учетом времени: NLP модели | Время можно использовать как фичу и юзать дискретно или непрерывно | Контентные фичи дают прирост, но сложны | Оффлайн и онлайн метрики часто не коррелированы и нужно следить за ними


## Lecture 1. Introduction

- slide 1: Introduction to RecSys
- slide 2: Why RecSys are needed | 1. Enhancing User Experience | Recommender systems tailor content to individual user preferences | It reduces search time of user and increases user satisfaction | 2. Increasing User Engagement and Retention | Recommender systems keeps users engaged with a platform for longer periods. | This sustained engagement encourages repeat visits, fostering customer loyalty and reducing churn rates ( | Retention) | . | 3. Boosting Sales and Revenue | By understanding user preferences, businesses can leverage targeted ads and advertisements to achieve increased sales.
- slide 3: Difference between RecSys and Information Search | Information Retrieval | Operates based on an explicit user query. | Focuses on relevance to the query rather than personalization on user. | Information Retrieval | Operates based on an explicit user query. | Focuses on relevance to the query rather than personalization on user.
- slide 4: Introduction myself | I was DS in o | ut-of-network recommendations in VK Team for 3 years | I’m working in startup of Majoritas | I was learning in CSC and got Master’s degree(where Jetbrains was a sponsorship)
- slide 5: About the course | You will have three HW and little project | Don’t have an exam | The first HW after the second/third lecture
- slide 6: History of RecSys
- slide 7: History of RecSys | October 2, 2006: start | competition “Netflix prize” from | company Netflix | Netflix was a company as a DVD shop | Decrease RMSE | Task: predict rating from 1 to 5 | Dataset: 17_700 films, 480К users, | 100M feedback | https://sifter.org/simon/journal/20061211.html
- slide 8: History of RecSys | Metric in Train: | Metric in Test:
- slide 9: History of RecSys
- slide 10: Problem formulation
- slide 11: General problem formulation | Two main objects: | - Users | - Items – | products/musics/videos
- slide 12: General problem formulation
- slide 13: General problem formulation
- slide 14: Task
- slide 15: Task: Binary classification | Like – 1, Dislike – 0. | You must predict 0/1 for every item for current user.
- slide 16: Task: Regression | Predict rating r_ui for every item.
- slide 17: Task: Ranking | It is enough to own user and a set of objects to rearrange these objects in order of destruction of the rating. | A | ranking model | is used to solve this task
- slide 18: Spoiler: Types of ranking | *we don’t have a query q, it is from information retrieval
- slide 19: Milestone
- slide 20: Dataset
- slide 21: Dataset: Explicit Feedback | User clearly appreciated the item | Very little such data
- slide 22: Dataset: Explicit Feedback | User bias: | One user likes to rate | in range of 1-3. | Other user likes to rate in range of 4-5. | Item bias: effect of Harry Potter
- slide 23: Dataset: Implicit Feedback | You can check: how long the user watched this video | The user paused over the post while rewinding | You can see on clicks of user
- slide 24: Dataset: Implicit Feedback | A lot of data | Very noise data | You can have clickbaits
- slide 25: Dataset: Implicit Feedback | Clickbait | Yellow news
- slide 26: Milestone
- slide 27: Algorithm
- slide 28: Algorithm: Matrix factorization
- slide 29: Algorithm: Matrix factorization
- slide 30: Algorithm: Matrix factorization | We have sparse matrices
- slide 31: Algorithm: Matrix factorization | We can’t make matrix factorization directly, because we don’t know a lot data
- slide 32: Algorithm: Matrix factorization | We can’t make matrix factorization directly, because we don’t know a lot data
- slide 33: Algorithm: Matrix factorization | After | training | we have item and user embeddings
- slide 34: Method of recommendations | Recommendation | Item2Item | User2User
- slide 35: Method of recommendations: Item2Item | Item2Item recommendations
- slide 36: Item2Item/User2User
- slide 37: Algorithm: Collaborative filtering | set of methods based on user’s feedbacks
- slide 38: Milestone
- slide 39: Calculate rating
- slide 40: Cosine similarity
- slide 41: Milestone
- slide 42: Problems of CF | Doesn’t use additional information about items and users (without user and item features) | Doesn’t work with new users and new items (problem of cold start) | We will have feedback loop
- slide 43: Feedback loop | User gives dataset | We use dataset for training | We give recommendations | User can’t see new categories
- slide 44: Cold start
- slide 45: Cold start | New users, new items without data for collaborative filtering
- slide 46: Cold start: LightFM
- slide 47: Pipeline
- slide 49: Reranking | Reduce count of long videos | Business tasks: boosting some groups, ads | Other candidate source: for example, popular items
- slide 50: Candidate selection
- slide 51: Content-based
- slide 52: Content-based
- slide 53: Types of algorithms
- slide 54: Multi-armed bandits
- slide 55: Multi-armed bandits | an agent must choose between different actions (arms) to maximize cumulative reward | In a recsys, each arm represents a different recommendation (movie, product, etc.), and the reward represents user interaction (click, purchase, like, etc.).
- slide 56: Multi-armed bandits | an agent must choose between different actions (arms) to maximize cumulative reward | In a recsys, each arm represents a different recommendation (movie, product, etc.), and the reward represents user interaction (click, purchase, like, etc.).
- slide 57: Multi-armed bandits | you can have few multi-armed bandits for different genders
- slide 58: Multi-armed bandits | you can have few multi-armed bandits for different ages
- slide 59: Word2Vec
- slide 60: Word2Vec | Word2Vec is learning sequence of words
- slide 61: Word2Vec for recommendations | Word2Vec is learning sequence of items (history of users)
- slide 62: From simple to hard
- slide 63: Spoiler: properties | Diversity (not only cats) | Novelty (reels in Instagram) | Coverage(for candidate selection) | Serendipity
- slide 64: Final milestone


## Lecture 2. Matrix factorizations

- slide 1: Matrix factorizations
- slide 2: Two stages of RecSys
- slide 3: Collaborative filtering
- slide 4: SVD
- slide 5: Compressed embedding | Features: size, | weight | , count of eyes | If you need to reduce n-dimensional embedding, you can | remove features with small dispersion
- slide 6: Task | SVD can compress data with changing spaces
- slide 7: SVD
- slide 8: Truncated SVD | https://timbaumann.info/svd-image-compression-demo/
- slide 9: Candidate selection
- slide 10: Truncated SVD | https://timbaumann.info/svd-image-compression-demo/ | k = 20 | k = 100
- slide 11: Truncated SVD | with some k &lt;&lt; rank R
- slide 12: Truncated SVD | similar tasks
- slide 13: Truncated SVD | L | =
- slide 14: Truncated SVD | Loss | = | С_i for regularization of user popularity | С_j for regularization of item popularity
- slide 15: SVD | Prediction:
- slide 16: SVD | Prediction: | Loss function:
- slide 17: SVD | Prediction: | Loss function: | Loss function + regularization:
- slide 18: Milestone
- slide 19: ALS
- slide 20: ALS | Initialize X and Y with random values | for loop: | f | ix matrix Y(items) | s | earch optimal matrix for X(users) | fix matrix X(users) | search optimal matrix for Y(items)
- slide 21: ALS: step 1 in for loop
- slide 22: ALS: | step 2 in for loop
- slide 23: ALS: Analytical decision with step by X(users)
- slide 24: ALS | : Analytical decision with step by X(users)
- slide 25: ALS | : Analytical decision with step by X(users)
- slide 26: ALS | : Analytical decision with step by X(users)
- slide 27: ALS | : Analytical decision with step by X(users)
- slide 28: ALS | : Analytical decision with step by X(users)
- slide 29: ALS | : Analytical decision with step by X(users)
- slide 30: Milestone
- slide 31: IALS
- slide 32: IALS | preference
- slide 33: IALS | preference | confidence
- slide 34: IALS | preference | confidence | l | oss
- slide 35: IALS
- slide 36: IALS | : Analytical decision with step by X(users)
- slide 37: IALS | : Analytical decision with step by X(users)
- slide 38: IALS | b i | , | bj bias of user and item
- slide 39: Milestone
- slide 40: BPR
- slide 41: BPR: Idea | Task: ranking | Observed data is positive items | No observed and negative data are negative | We can use pairs of items: one item is positive, second item is negative
- slide 42: BPR: Idea of algorithm | maximizing of posterior probability of a user preferring a positive item (one the user interacted with) over a randomly chosen negative item
- slide 43: BPR: Create dataset | Dataset (u,i,j) for training model:
- slide 44: BPR: Create dataset | Dataset (u,i,j) for training model | We need to make such datasets for every users
- slide 45: BPR: Loss | function | AUC can be good loss, however it hasn’t gradient
- slide 46: BPR: Loss function
- slide 47: BPR: Algorithm
- slide 48: Gradient | We only want to solve if the user would rate the item i higher than the item j
- slide 49: Milestone
- slide 50: WARP
- slide 51: WARP | The goal of WARP is to minimize not just the error between the predicted and the true value, but the rank of positive examples relative to negative ones, making it more sensitive to the item's position in the recommendation list.
- slide 52: FUNKSVD
- slide 53: FUNKSVD | g | eneral formula:
- slide 54: SVD++, timeSVD++
- slide 55: SVD++, timeSVD++ | SVD++ | timeSVD++
- slide 56: Hello everyone! Welcome to the Recommendation Systems course! | In this course, you’ll learn what recommendation systems are, why they are useful, and how they work on different platforms. | We’ll focus on key algorithms, mainly matrix factorization and ranking. | The course includes lectures and summaries. Watch the lecture first, then read the summary to better understand the topic. After that, you can answer the questions at the end of the module.


## Lecture 3. Metrics

- slide 1: Metrics
- slide 2: Metrics
- slide 3: Metrics
- slide 4: Offline metrics
- slide 5: RMSE
- slide 6: Precision, Recall
- slide 7: Precision, Recall
- slide 8: Precision, Recall
- slide 9: Problem: Precision, Recall | model 1 | model 2 | ==
- slide 10: Problem: Precision, Recall | model 1 | model 2 | ==
- slide 11: AUC | AUC is | probability | that random pair will be ordered correctly
- slide 12: AUC | AUC is probability that random pair will be ordered correctly | Other interpretation:
- slide 13: Precision@k, Recall@k
- slide 14: AP@k
- slide 15: DCG, NDCG | These metrics think about position of items | The first position is most expensive
- slide 16: Online metrics
- slide 17: Some online metrics | DAU = count of daily active users | MAU = count of | monthly | active users | Scroll Depth
- slide 18: SLIM
- slide 19: Sparse Linear Model | Fast linear model | A – matrix of user-item | interactions(clicks or shows) | Constraints: w_ij &gt;= 0 and w_ii = 0
- slide 20: Loss function | Goal: finding the same items | We can make a parallelization by rows:
- slide 21: FM
- slide 22: Factori
- slide 24: FFM


## Lecture 4. Content based

- slide 1: Content-based models
- slide 2: Pipeline
- slide 3: Airflow
- slide 4: Airflow
- slide 5: SLIM
- slide 6: SLIM(Sparse Linear Methods) | A | is a binary matrix M x N of user-item interactions with clicks/shows | Weights f for removing simple decision | – predicted rating
- slide 7: Loss function | Loss function for training this model:
- slide 8: Loss function | Loss function for training this model: | We can make a parallelization by rows:
- slide 9: Factorization Machine
- slide 10: Factorization machine | n | = |I| + |U| | – features | – one-hot vectors of the user-item pairs
- slide 11: Factorization machines | n = |I| + |U| | – features | – one-hot vectors of the user-item pairs
- slide 12: Factorization Machine | We have W – our weights
- slide 14: Count of pairs:
- slide 15: Factorization Machine | For saving memory, we can introduce as , | where V – matrix n x k | Count of parameters: n + k + 1
- slide 16: Factorization Machine
- slide 17: Factorization Machine | We have such final equation: | It is a factorization machine
- slide 18: Field-aware Factorization Machine
- slide 19: Field-aware Factorization Machine | We can have different interactions between different pairs. Example (year, car), (year, color) | We can separate such interactions | For every feature we have different embeddings
- slide 20: Field-aware Factorization Machine
- slide 21: Field-aware Factorization Machine | We have W – our weights
- slide 22: DSSM
- slide 23: DSSM(deep semantic | similarity | model) | SGD for training | Scalar product was for getting predicted rating | We can use other ways here
- slide 24: DSSM(deep semantic similarity model) | SGD for training
- slide 25: DSSM | Q – text query, D – document | and vectors from bag of words | Using NN we can get user and item embedding | Scalar product/cosine similarity are for ranking
- slide 26: Training of DSSM | We can use all data about item and user
- slide 27: Training of DSSM | Probability of click to document for this query: | where:
- slide 28: Training of DSSM | Probability of click to document for this query: | where: | Loss function:
- slide 29: Training of DSSM | Probability of click to document for this query: | = | Negative sampling:
- slide 30: Training of DSSM | Probability of click to document for this query with negative sampling: | Loss function:
- slide 31: Cross-entropy loss | Calculating | Loss function:
- slide 32: Pairwise loss | We have (u, item1, item2), where item1 is positive, item2 is negative
- slide 33: Pairwise loss | We have (u, item1, item2), where item1 is positive, item2 is negative(as BPR) | We can make some threshold(as WARP):
- slide 34: Full product Softmax Loss | Take batch of (u, w, r) with size M | matrix of users | matrix of items | vector of ratings | We will see the matrix:
- slide 35: Full product Softmax Loss
- slide 36: Full product Softmax Loss
- slide 37: Only cosine similarity
- slide 38: Training process in multi-gpu
- slide 39: Transformers
- slide 41: Encoder


## Lecture 5. Sequential models

- slide 1: Lecture 5. Sequential models
- slide 2: Youtube DNN [2016] | Youtube was the first in showing own architecture, | YoutubeDNN | YoutubeDNN is separated to two stages: candidate generation and ranking | Link
- slide 3: YoutubeDNN: First stage | Multiclassification is for training | Every class – video_id | Link
- slide 4: Youtube DNN | training process | inference | Link
- slide 5: YoutubeDNN: Second stage | It is ranking stage for 100 candidates | Link
- slide 6: Deep interest Network
- slide 7: Deep Interest Network(Alibaba) | We will solve binary classification(click/not click)
- slide 8: Deep Interest Network(Alibaba)
- slide 9: Function of activation
- slide 10: Deep Interest Network | Changing of loss function:
- slide 11: Deep Interest Network
- slide 12: Deep Interest Network
- slide 13: SasRec
- slide 14: Self-Attentive Sequential Recommendation | unidirectional | model | Model has a self-attention layer | Link
- slide 15: Self-Attentive Sequential Recommendation | Link
- slide 16: SasRec: Datasets for checking | Link
- slide 17: Link
- slide 18: Link
- slide 19: Bert4Rec
- slide 20: Bert4Rec | Link
- slide 21: Link
- slide 22: Link
- slide 23: Bert4Rec: training | process | Link | random masked items | is the true item for the masked item | masked version of user history
- slide 24: PinSage
- slide 25: PinSage | Link | 350M+ monthly active users interact with 2B+ visual bookmarks | User can have different interest | If you mean vectors, you will get no relevant object
- slide 26: PinSage | Link
- slide 27: PinSage | Link
- slide 28: PinSage | Link | Batch inference | is data for 90 days | Light Weight Real-time inference | : last 10 actions of user
- slide 29: PinnerFormer
- slide 30: PinnerFormer | Link
- slide 31: PinnerFormer | Link | scalar product with time
- slide 32: PinnerFormer | Link
- slide 33: PinnerFormer | Link
- slide 34: Transformers
- slide 35: Transformers | Encoder | Decoder
- slide 36: Transformers | Encoder | is Self-attention and Neural Network
- slide 37: Transformers | Encoder | is Self-attention and Neural Network
- slide 38: Transformers
- slide 39: Transformers
- slide 40: Transformers
- slide 41: Transformers
- slide 42: Transformers
- slide 43: Transformers
- slide 44: Transformers
- slide 45: Transformers
- slide 46: Transformers
- slide 47: BERT


## Lecture 6. Ranking

- slide 1: Learning to rank
- slide 2: General problem formulation
- slide 3: Task
- slide 4: Task: Binary classification | Like – 1, Dislike – 0. | You must predict 0/1 for every item for current user.
- slide 5: Task: Regression | Predict rating r_ui for every item.
- slide 6: Task: Ranking | It is enough to own user and a set of objects to rearrange these objects in order of destruction of the rating. | A | ranking model | is used to solve this task
- slide 7: Spoiler: Types of ranking | *we don’t have a query q, it is from information retrieval
- slide 8: Training process
- slide 9: Training process
- slide 10: Training process
- slide 11: Pipeline of recsys
- slide 12: Gradient Boosting | Composition of trees: | Every next model tries to predict difference y_target - y_pred
- slide 13: Gradient Boosting
- slide 14: RankNet
- slide 15: Learning to rank | RankNet, LambdaRank, LambdaMART, YetiRank
- slide 16: RankNet: Task | Probability that item | s_i is more relevant than item s_j | Use
- slide 17: RankNet: Loss | Loss function:
- slide 18: RankNet: Loss | Loss function: | Label | : | S_ij = 1, if i &gt; j | 0, if i = j | -1, if i &lt; j
- slide 19: RankNet: Loss | Loss function: | Label: | S_ij = 1, if i &gt; j | 0, if i = j | -1, if i &lt; j | Probability | :
- slide 20: RankNet: Loss | Loss function:
- slide 21: RankNet: Loss | Loss function: | Gradient calculation:
- slide 22: RankNet: factorization
- slide 23: RankNet: factorization
- slide 24: RankNet: linear complexity | Lambda vector i – aggregation by all pairs with item i | Lambda vector – vector is calculated for every document: | direction: you need to move document to up or down for getting better ranking | length of vec is size of moving
- slide 25: RankNet: Problems | Example: mistake in pair (1, 99) | Example: mistake in pair (97, 98)
- slide 26: RankNet: Problems | Example: mistake in pair (1, 99) | Example: mistake in pair (97, 98) | Decision: optimize some metric as NDCG
- slide 27: LambdaRank
- slide 28: LambdaRank | Loss(RankNet + NDCG):
- slide 29: LambdaRank | LambdaRank tries to maximize NDCG | RankNet tries to minimize | count of errors in pairs
- slide 30: LambdaMart
- slide 31: LambdaMart | LambaMart = LambdaRank + MART | MART – family of models for tasks of classification, regression, ranking.
- slide 32: YetiRank
- slide 33: YetiRank | Not all pairs are important | The most important pairs at the top of list | We need the confidence of model, that item i more relevant than item j
- slide 34: YetiRank | XGBoost (LambdaMART, …) | https://xgboost.readthedocs.io/en/latest/parameter.html | CatBoost (YetiRank, …) | https://catboost.ai/en/docs/concepts/loss-functions-ranking#pairwise-objectives-and-metrics | LightGBM (LambdaRank, …) | https://lightgbm.readthedocs.io/en/latest/Parameters.html | RankNet, LambdaRank на PyTorch | https://github.com/haowei01/pytorch-examples/tree/master/ranking


## Lecture 7. Highload service

- slide 1: Lecture 7. | Highload service
- slide 2: Pipeline | Pipeline of working our recommendation system
- slide 3: Logging
- slide 4: Logging | For training model we need to save actions of users in some structure | We need “user-item-rating-timestemp”
- slide 5: Hadoop
- slide 6: Hadoop: | Scalability | Some data: relational database(SQL, MySQL) in one machine. | A lot of data: | 1) Vertical scalability | 2) Horizontal scalability
- slide 7: Hadoop: Database | Separate File in to blocks | Save these blocks in different machines | When you need to get calculation, you can
- slide 8: Hadoop: Database | Two types of Nodes: | 1) NameNode – info, which Datanode is saving this block | 2) DataNode – saving some blocks
- slide 9: MapReduce paradigm | You can make some action in local machine(Map) | Aggregate answers from all machines(Combiner) | Make some action(Reduce)
- slide 10: MapReduce paradigm
- slide 11: Hadoop: training model
- slide 12: Training ALS | R = XY, we need to update X | Algorithm: | - Join R and Y by items → (u, r_ij, y_i) | Group by u | In every machine we calculate x_u
- slide 13: Training ALS: broadcast | Example: Spark ML
- slide 14: Training ALS: broadcast
- slide 15: Reliability
- slide 16: Reliability
- slide 17: Kafka
- slide 18: Kafka
- slide 20: Quantization
- slide 21: Speed of training | Default type: float32 | float32 → uint8 | FP16: float32 → float16
- slide 22: User loading
- slide 23: Cache | Caching recommendations for users
- slide 24: Cache | Smart | Caching recommendations for users | Use special model for understanding relevance of | recommendations | in a cache
- slide 25: Sharding
- slide 26: Sharding
- slide 27: Monitoring
- slide 28: Monitoring | You can control your service | Grafana is a popular tool | Alert management
- slide 29: Key-value storage
- slide 30: Pipeline | Pipeline of working our recommendation system
- slide 31: Key-value storage | We need fast saving data | Such key-value, which can work for O(1) for write/read | Eventual consistency | Apache Cassandra, Amazon DynamoDB, Redis
- slide 32: KNN-index
- slide 33: Navigable Small World(NSW)
- slide 34: Navigable Small World(NSW)
- slide 35: Navigable Small World(NSW)
- slide 36: Navigable Small World(NSW)
- slide 37: HNSW | Malkov Y. A., Yashunin D. A. Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs //IEEE transactions on pattern analysis and machine intelligence. – 2018.


## Lecture 8. GNN

- slide 1: Properties of Recsys
- slide 2: Coverage
- slide 3: Properties: Coverage | |I_rec| — count of recommended objects | |I| – count of all objects
- slide 4: Novelty
- slide 5: Properties: Novelty | Idea: | the less popular an item is, the more likely it is to be new to the user | Theory of information: P_i = m_i/N, where | m_i count of users, who showed this object, N – count of all users
- slide 6: Diversity
- slide 7: Properties: Diversity | R – recommended items | sim(i, j) – cosine similarity between two items | Goal: to minimize this metric
- slide 8: Serendipity
- slide 9: Properties: Serendipity | Goal: to recommend relevant items + user didn’t have the similar items before
- slide 10: Properties: Serendipity | if the Pr model is confident that the user will like item i, more than the confidence of a primitive model, this means that this user may especially like item i.
- slide 11: Properties: Serendipity | For increasing this metric, you need: | add more features for pairs (user, object); | weigh targets to more accurately account for unusual clicks/views; | write custom loss functions that will reward the model for boosting unexpected objects.
- slide 12: Netflix case study
- slide 13: Netflix case study | Main metric: user’s retention | They try to make good diversity with using different models
- slide 14: RBM
- slide 15: RBM | Restricted Boltzmann Machine: one of the prizers from Netflix prize competition | 2 layers: second layer tries to understand distribution of data | Inference: unstable recommendations
- slide 16: RBM | Input: multi-hot vector of user interactions | Output: recommendations
- slide 17: Autoencoder
- slide 18: Autoencoders | Autoencoder consists of two parts: | Encoder: input vector | X | converts to low-dimensional vector | Decoder: | low-dimensional vector converts to original input vector | X’ | Main goal: minimize diff(X, X’)
- slide 19: Autoencoders | Autoencoder consists of two parts: | Encoder: input vector | X | converts to low-dimensional vector | Decoder: low-dimensional vector converts to original input vector | X’ | Main goal: minimize diff(X, X’)
- slide 20: Autoencoders | Matrix factorization | Asymmetric | matrix factorization: | Matrix factorization through autoencoders
- slide 21: Autoencoders: item2item | dimension of hidden vector can be equal to dimension of input vector | You can use hidden vector for item2item task
- slide 22: Autoencoders: deep forward model | We can reduce dimension of output vector and train so | Our model will understand the current relevant items
- slide 23: Autoencoders: deep forward model | History is as a sentence | LSTM, GRU, BERT for training
- slide 24: Using time as | discrete | / | continuous | value | Discrete time: day, week, month | Continuous | time: time
- slide 25: Main ideas of history
- slide 26: Friend prediction model step-by-step
- slide 27: Task | Task: friend recommendation | T | he friend recommendation system is a key element to decide if a social media platform can attract more users. | Friend recommendation has traditionally been done with methods like graph-based heuristics.
- slide 28: Dataset description
- slide 30: Dataset | Dataset | We use Facebook social circles data. | The dataset includes node features (profiles), circles, and ego networks.
- slide 31: Dataset | Dataset | “Ego” means the owner of the network. | The ego user may form circles based on common bonds and attributes between themselves and the users whom they follow. | In the figure above, the central user (the ego) is friends with all other users in the network. There are 5 circles annotated on the graph: friends under the same advisor, CS department friends, college friends, family members, and high school friends. The circles may overlap.
- slide 32: Dataset | Dataset | For the simplicity of this project, we will only use one of the ego networks in the dataset (e.g. the ego network for User 0). | The graph is composed of 347 nodes and 5038 edges. | Each node is represented by a 224 dimension feature vector.
- slide 33: Dataset | Dataset | For the simplicity of this project, we will only use one of the ego networks in the dataset (e.g. the ego network for User 0). | The graph is composed of 347 nodes and 5038 edges. | Each node is represented by a 224 dimension feature vector.
- slide 34: Introduction to GNN
- slide 35: Model | One of the core concepts of GNN is node embeddings. | Tasks: node classification, link prediction, community detection, network similarity | For friend recommendations: link prediction
- slide 36: Model | The key idea of GNN is to generate node embeddings based on local network neighborhoods. | The model can be of arbitrary depth. | Every node has its embedding at each layer. | Layer-0 embedding of a node is its user feature. | Layer-k embedding gets information from nodes that are k hops away.
- slide 37: Model | During each message-passing iteration, the embeddings are updated by two steps: message computation and aggregation.
- slide 38: Model
- slide 39: SageConv | The layers of a GNN are designed to capture increasingly complex features of the graph by aggregating information from the neighborhood of each node.
- slide 40: Link prediction
- slide 41: Model | Friendship is all about connections in the graphs | We need to transform what we know about the nodes (users) into information about the edges (friendships) | Specifically, whether an edge exists in the graph or not.
- slide 42: Model | We can model this link prediction task as estimating a “likelihood” score to every potential edge. | One simple way to obtain this score is to take the dot product between the learned embeddings of two nodes.
- slide 43: Rank prediction
- slide 44: Model | Now, we can obtain the suggested list of friends for a given user. | For this user, we calculate the scores between the user and all other users that they’re currently not friends with. | Then we sort those users by the scores, taking the top K users to recommend to this user as potential friends.
- slide 45: Model
- slide 46: Experiments
- slide 47: Train-test split | Normally in a recommender systems setting, the testing set is split based on time. | For example, the train set contains all friendships formed up to 2020, and the test set contains all new friendships in 2021, which the model will try to predict.
- slide 48: Metrics | ranking-based metrics | classification-based metrics
- slide 49: Ranking-based metrics | Hitrate@k score
- slide 50: Classification metrics | AUC score
