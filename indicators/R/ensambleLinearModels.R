library("rjson")
source("indicators/R/createEnsambleModels.R")

# Fetch command line arguments
myArgs <- commandArgs(trailingOnly = TRUE)

result <- as.data.frame(fromJSON(myArgs[1]))

dataTrain  <- result[1:(nrow(result)-1),]
dataTest   <- result[nrow(result):nrow(result),]

resultHigh  <- GetComboEstimatorsLinearModels(dataTrain, dataTest, "high")$price
resultLow   <- GetComboEstimatorsLinearModels(dataTrain, dataTest, "low")$price
resultClose <- GetComboEstimatorsLinearModels(dataTrain, dataTest, "close")$price

# create 3 means predictors

# Estimadores de precio por media iterada 
open <- dataTrain$close[length(dataTrain$close)]
mediaEstimadorLow <- mean(resultLow[resultLow <  open] )
mediaEstimadorLow_iterada2 <- mean(resultLow[resultLow>mediaEstimadorLow & resultLow < open ] )
mediaEstimadorLow_iterada3 <- mean(resultLow[resultLow>mediaEstimadorLow_iterada2 & resultLow < open ] )
lowComboEstimations <- base::paste(resultLow, collapse=",")

# Estimadores de precio por media iterada 
mediaEstimadorHigh <- mean(resultHigh[resultHigh > open ] )
mediaEstimadorHigh_iterada2 <- mean(resultHigh[resultHigh<mediaEstimadorHigh & resultHigh > open ] )
mediaEstimadorHigh_iterada3 <- mean(resultHigh[resultHigh<mediaEstimadorHigh_iterada2 & resultHigh > open ] )
highComboEstimations <- base::paste(resultHigh, collapse=",")

# no se ejecutan trades mas chicos q esta media y un posible entorno
low_sum <- 0
high_sum <- 0
for (i in c(1:(length(dataTrain$close) - 1 ))) {
    open <- dataTrain$close[i]
    low <- dataTrain$low[i+1]
    low_sum <- low_sum + (open - low)
    high <- dataTrain$high[i+1]
    high_sum <- high_sum + (high - open)
}

diferencia_media_open_low <- low_sum / (length(dataTrain$close) - 1)
deltaMediaOpenLow <- open - diferencia_media_open_low

diferencia_media_open_high <- high_sum / (length(dataTrain$close) - 1)
deltaMediaOpenHigh <- open +  diferencia_media_open_high
  
mediaEstimadorClose <- mean(resultClose)
closeComboEstimations <- base::paste(resultClose, collapse=",")

returns <- base::paste(mediaEstimadorLow,mediaEstimadorLow_iterada2,mediaEstimadorLow_iterada3, deltaMediaOpenLow,lowComboEstimations,
                      mediaEstimadorHigh,mediaEstimadorHigh_iterada2,mediaEstimadorHigh_iterada3, deltaMediaOpenHigh,highComboEstimations,
                      mediaEstimadorClose,closeComboEstimations, sep = "_")

# Cuidado devuelve en formato cast string
# si es para certificar estructuras str(result) redonda 
# pero internamente R esta manejando los puntos flotantes
# cat(str(result))
# para enviar los resultados se concatena con sprintf y se mantienen la precision. 
# sprintf("%.5f", returns)
cat( returns )





