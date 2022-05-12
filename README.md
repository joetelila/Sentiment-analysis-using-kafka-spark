# Sentiment-analysis-using-kafka-spark
Twitter sentiment analysis using Apache Kafka, Apache Spark structured streaming and dashboard monitoring page.


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#modules">Modules</a>
      <ul>
        <li><a href="#kafka_producer">Kafka Producer</a></li>
        <li><a href="#kafka_consumer">Kafka Consumer</a></li>
        <li><a href="#kafka_consumer">Web server</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img class="center" src="https://user-images.githubusercontent.com/40062131/168147166-e75c245e-e9a2-454b-8daa-6958a628dc27.png" width="70%" height="70%" alt="some_text">

This project is for `Distributed enabling platforms course 21/22 A.Y` at `unipi` given by `Prof. Patrizio Dazzi`. In this project, I implemeted tweet sentiment analysis using distributed systems. Technologies used will be listed below. In this project you will find three separated modules (applications).
* `Kafka-producer` : This module reads tweets from twitter API and publish tweets to kafka topic continously.
* `Kafka-consumer` : This is a spark application which uses spark structured streaming. It reads tweets from kafka server and make a prediction for each tweets and aggrigate the total tweet predicted for each sentiments(posetive, negative or neutral) and `POST` result to the web-server
* `web-server` : web-server is a flask web admin dashboard where all the total amount of tweets predicted and additional information are displayed

### Technologies user

I have utilized the following libraries for the development of this project.

* [Spark](https://spark.apache.org/downloads.html)
* [Kafka](https://kafka.apache.org/downloads)
* [Flask](https://flask.palletsprojects.com/en/2.1.x/)
* [Johnsnowlab Spark NLP](https://www.johnsnowlabs.com/spark-nlp/)

<!-- GETTING STARTED -->
## Getting Started
Loading ...

<!-- --------------------------------- uncomment this line ---------
This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
Loading . . .
<!----------------------------------uncomment this line ------
Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->
## Contact
Website - [joetelila.com](https://joetelila.com) 

Project Link: [https://github.com/joetelila/Sentiment-analysis-using-kafka-spark](https://github.com/joetelila/Sentiment-analysis-using-kafka-spark)

