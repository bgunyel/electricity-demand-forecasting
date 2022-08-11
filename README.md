# Electricity Demand Forecasting

***This project is being actively developed. Stay tuned!***

## Table of Contents
* [Introduction](#introduction)
* [Data Analysis](#data-analysis)
  - [Examination of Covid-19 Impact](#examination-of-covid-19-impact)
  - [Examination of Schools' Impact](#examination-of-schools-impact)
  - [Examination of Ramazan Impact](#examination-of-ramazan-impact)
  - [Extracted Features and Data Pre-Processing](#extracted-features-and-data-pre-processing)
* [Forecasting Algorithms](#forecasting-algorithms)
* [Experimental Results](#experimental-results)

## Introduction
In the rapidly developing world, energy needs are increasing at the same pace. Since the industrial revolution, countries with access to energy resources have come to economically strong positions. On the other hand, the ever-increasing macro-economic and micro-economic competition between different entities is forcing the absolute need for efficient energy use in order to achieve economic efficacy and/or efficiency.

On the other hand, the global sustainable growth need has brought new opportunities and challenges hand-in-hand. Regulatory bodies have been forcing economic entities to use green energy sources more than non-green ones. Additionally, economic entities are encouraged to use green energy sources more efficiently.
Electricity, being relatively easy to transmit, has had ever-increasing use globally. Switching the electricity production mainly from non-green to green processes increases its potential for sustainability-oriented development. On the other hand, the relative inefficiency and higher cost of storing electrical energy make the instant balancing of demand and supply extremely important. 

For some product or service categories, deciding whether supply follows demand or demand follows supply can be regarded as a chicken-egg problem of economics. However, supply follows demand due to the need for instant balancing in the electricity market. Hence, for both producers and regulators, it is of utmost importance to have an excellent understanding of demand. An accurate demand forecast satisfies this need.

Electricity demand forecasting can be beneficial in different time horizons. For example, for an economic entity considering its existence in the long-term, a demand forecast with monthly or yearly resolution would be the most appropriate. In addition, for a producer trying to make operational adjustments in the near future, forecasting the daily demand for the upcoming week or fortnight would be beneficial.

On the other hand, an electricity producer who has to give hourly offers on the supply side in the Day-Ahead Market is primarily interested in the hourly forecasts for the next 24 hours. Similar models (if not the same) can be utilized for applications in these different time horizons with training with appropriate data.

Spot markets are divided into two; Day-Ahead Market (DAM) and Intra-Day Market (IDM). The DAM is the market where the electricity price for each hour of the next day is determined by auction and has a larger transaction volume. On the other hand, IDM enables the participants to change their position in the Day-Ahead Market for a certain amount of time before electricity is physically transmitted. Any imbalance in the electricity grid caused by a mismatch of demand and supply is compensated after the closure of the IDM. Hence, having precise demand forecasts will provide high value to all parties in the electricity market.

This project proposes an algorithm and implementation for forecasting hourly demand in the next 24-hour time frame. The forecasting system can be utilized by market players on the supply side and the regulatory bodies most interested in balancing the supply and demand. The system is trained and tested on Turkish electricity market data and hence, very few features are special to Turkey. Nevertheless the system can be utilized in any electricity market with minimal modifications (and re-training).

## Data Analysis

Data used in this project is obtained from the official website of Energy Exchange Istanbul (EXIST) or Enerji Piyasaları İşletme A.Ş. (EPİAŞ) by its Turkish name ([EXIST / EPIAS. (2022)](#epias-2022)). Therefore, the two acronyms EXIST and EPİAŞ will be used interchangeably.

Hourly electricity demand data between 2017-01-01 and 2022-06-30 are utilized in this study. For a visual introduction, the following figure presents the hourly electricity consumption in Turkey between 2022-04-01 and 2022-06-30.

![hourly_2022-04-01_2022-06-30](./images/hourly_2022-04-01_2022-06-30.png)

As seen in the above figure, the electricity consumption shows regular patterns, higher during business days than weekend days. The sharp drop at the beginning of May reflects the lower electricity usage during the Ramazan Feast.

The daily pattern in demand (in MWh) can be seen in the following figure.

![daily-average-consumptions](./images/daily-average-consumptions.png)

As expected, the business days have higher average consumption than weekend days. In addition, Saturdays, which are a working day in some companies, have higher average consumption than Sundays. On the other hand, the intra-day consumption stays at the highest level between 10 am and 8 pm.

### Examination of Covid-19 Impact

One recent question that deserves attention is whether the Covid-19 Pandemic impacts electricity consumption. For this purpose, the years 2017, 2018, and 2019 are labeled “Before Covid”, whereas 2020 is marked as “During Covid”. On the other hand, the years 2021 and 2022 are examined as “After Covid.” The following figure shows the daily averages (MWh) corresponding to those groups.

![daily-average-consumptions_covid](./images/daily-average-consumptions_covid.png)

Careful examination of the above figure reveals that the general pattern between business days and weekend days is preserved before, during, and after Covid. In addition, the consumption stays close to its peak level between 10 am and 8 pm in all of the sub-figures. However, there is a definite increase in the general level of electricity consumption after Covid, when compared with consumption before Covid and during Covid. 

Is this an impact of the Covid Pandemic, or is there already an increasing trend throughout the years? The following figure shows the average daily consumption for all years separately.

![daily-averages_all-years](./images/daily-averages_all-years.png)

A careful examination of the above figure reveals that there is not a clear increasing trend in consumption throughout 2017, 2018, and 2019. On the other hand, electricity consumption in 2021 is slightly higher than in 2022. Therefore, although the consumption after Covid (2021 & 2022) is higher than the consumption in previous years, any apparent reason could not be found in this analysis.

### Examination of Schools' Impact

One other interesting question to examine is whether schools have a significant impact on electricity consumption. For this purpose, the following figure shows the 7-day rolling average of daily electricity consumption for different years.

![schools-impact](./images/schools-impact.png)

Having a careful look at the above figure reveals an interesting relationship between school closure dates and electricity consumption. It is evident that electricity consumption generally is higher when the schools are closed. This can easily be explained by the fact that most of the school closures happen in summer when electricity consumption increases due to cooling needs. Although there is only a correlation but no causation relationship between schools and electricity consumption, this is most of the time more than enough for a machine learning algorithm which is the backbone of forecasting.

### Examination of Ramazan Impact

Another interesting question to analyze is whether Ramazan has a significant impact on electricity consumption. For this analysis, the following figure presents the 7-day average of daily electricity consumption separately for each year. Days falling in Ramazan are indicated with a marker (*).

![ramazan-impact](./images/ramazan-impact.png)

This is not an easy question to answer with only 6 years of data because Ramazan is sliding backward by 10-11 days every year. According to the above figure, electricity consumption increases throughout Ramazan and makes a peak just before Ramazan Feast in 2017, 2018, 2019, and 2020. On the other hand, this behavior is not observed during Ramazan in 2021 and 2022. It is not very easy to separate whether this behavior depends on Ramazan's sliding characteristic or is just a coincidence. More data should be examined to find a statistically significant answer.

### Extracted Features and Data Pre-Processing

The following features are extracted for each data sample:

* week_day:
  - Monday:1
  - Tuesday:2
  - Wednesday:3
  - Thursday:4
  - Friday:5
  - Saturday:6
  - Sunday:7
* weekend:
  - 1 if the sample day is a weekend day
  - 0 else
* year:
  - year of the data sample
* month:
  - the month of the sample between [1, 12]
* day:
  - day of the sample within the month (between [1, 31])
* hour:
  - hour of the data sample between [0, 23]
* quarter:
  - January, February, March: 1
  - April, May, June: 2
  - July, August, September: 3
  - October, November, December: 4
* schools_closed:
  - 1 if the schools are on holiday
  - 0 else
* ramazan:
  - 1 if the sample is in Ramazan
  - 0 else
* holiday:
  - 1 if the day of the sample is on holiday (national or religious)
  - 0 else
* before_after_holiday:
  - 1 if the day of the sample is either just before or just after a holiday
  - 0 else
* bridge_day:
  - 1 if the day of the sample is a bridge day
  - 0 else

The interested reader can consult ([Erişen, 2013](#erisen-2013)) for more details on feature extraction.

The whole data set is split as follows:

* __train set:__ [2017-01-01, 2021-12-31]
* __validation set:__ [2022-01-01, 2022-03-31]
* __test set:__ [2022-04-01, 2022-06-30]

For each sample, the consumption data is normalized to zero-mean and unit standard deviation. For this purpose, the mean and standard deviation computed over the training set is utilized. For the year feature, min-max scaling is applied.

Sine and cosine transforms are applied for the features week_day, month, day, hour, and quarter.

* week_day_sine = sin(2π * week_day / 7)
* week_daycos = cos(2π * week_day / 7)
* month_sine = sin(2π * month / 12)
* month_cos = cos(2π * month / 12)
* day_sine = sin(2π * day / 31)
* day_cos = cos(2π * day / 31)
* hour_sine = sin(2π * hour / 24)
* hour_cos = cos(2π * hour / 24)
* quarter_sine = sin(2π * quarter / 4)
* quarter_cos = cos(2π * quarter / 4)


## Forecasting Algorithms

Taking an ordered set of input samples and generating an ordered set of outputs is defined as sequence-to-sequence learning in the field of machine learning ([Sutskever, 2014](#sutskever-2014)) and has long been known, especially in natural language processing (NLP) domain ([Cho, 2014-a](#cho-2014-a), [Cho, 2014-b](#cho-2014-b)). In recent years, there have been some studies that apply sequence-to-sequence learning to solve multi-step forecasting problems in time-series data ([Phandoidaen & Richter, 2020](#phandoidaen-2020)). 

Sequence-to-sequence learning methods are studied in this project due to their superiority in multi-step forecasting problems.

### Encoder-Decoder Architecture

The general architecture of an encoder-decoder system can be viewed in the following figure ([Kumaran, 2020](#kumaran-2020)). 

![encoder-decoder](https://miro.medium.com/max/700/1*62xsdc5F5DNdLXluQojeBg.png)

One important point to note is that this drawing is a “time-unrolled” scheme, meaning that there is only one GRU Cell in the Encoder and there is only one Decoder Cell in the Decoder. The GRU Cell and the Decoder Cell carries “hidden state” information from the previous time instant to the next. The advantage of using time-unrolled drawing in architectures that include recurrent neural networks (RNN) is that it improves understanding of the logic behind training. Encoder-Decoder architectures can be implemented with vanilla RNNs ([Dupond, 2019](#dupond-2019)), Gated Recurrent Units (GRU) ([Cho, 2014-b](#cho-2014-b)) or Long Short-Term Memory RNNs (LSTM) ([Hochreiter & Schmidhuber, 1997](#hochreiter-schmidhuber-1997)).

To have a general understanding, it will be beneficial to inspect the inner structure of vanilla RNN.


* $\sqrt{3x-1}+(1+x)^2$



## Experimental Results

TODO TODO TODO

## References

<a id="cho-2014-a"></a> 
Cho, K., van Merrienboer, B., Bahdanau, D., & Bengio, Y. (2014), 
_On the Properties of Neural Machine Translation: Encoder-Decoder Approaches,_
Eighth Workshop on Syntax, Semantics and Structure in Statistical Translation (SSST-8),
arXiv:1409.1259

<a id="cho-2014-b"></a>
Cho, K., van Merrienboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014),
_Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation,_
Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP),
arXiv:1406.1078

<a id="dupond-2019"></a>
Dupond, S. (2019),
_A thorough review on the current advance of neural network structures,_
Annual Reviews in Control, 14, 200-230

<a id="epias-2022"></a> 
EXIST / EPIAS. (2022), 
_EXIST Transparency Platform,_
https://seffaflik.epias.com.tr/transparency/

<a id="erisen-2013"></a> 
Erişen, E. (2013), 
_On the Parametric and Non-Parametric Prediction Methods for Electricity Load Forecasting,_ 
M.Sc. Thesis, Middle East Technical University

<a id="hochreiter-schmidhuber-1997"></a>
Hochreiter, S., & Schmidhuber, J. (1997),
_Long Short-term Memory,_
Neural Computation, 9(8), 1735-80

<a id="kumaran-2020"></a>
Kumaran, G. (2020, June 9),
_Encoder-Decoder Model for Multistep Time Series Forecasting Using PyTorch,_
Towards Data Science ([link to the article](https://towardsdatascience.com/encoder-decoder-model-for-multistep-time-series-forecasting-using-pytorch-5d54c6af6e60))

<a id="phandoidaen-2020"></a>
Phandoidaen, N., Richter, S. (2020),
_Forecasting time series with encoder-decoder neural networks,_
arXiv:2009.08848

<a id="sutskever-2014"></a>
Sutskever, I., Vinyals, O., & Le, Q. V. (2014),
_Sequence to Sequence Learning with Neural Networks,_
Proceedings of the International Conference on Neural Information Processing Systems, 2, 3104-3112

