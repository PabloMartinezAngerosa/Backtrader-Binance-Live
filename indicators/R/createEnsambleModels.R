GetComboEstimatorsLinearModels <- function(databaseTrain, databaseTest, nameVariablePredict) {
  
  # Algoritmo de fuerza bruta utilizado para encontrar el modelo con el  
  # minimo RMSE.
  # Buscamos todas las combinaciones posibles entre n variables.  
  
  #TODO hacer  dinamico con cantida de lags posibles. 
  
  .combinacionesPosibles <- tidyr::crossing(
    var1  = 0:1, 
    var2  = 0:1,
    var3  = 0:1,
    var4  = 0:1,
    var5  = 0:1,
    var6  = 0:1,
    var7  = 0:1,
    var8  = 0:1,
    var9  = 0:1,
    var10 = 0:1
  )
  
  .variablesLag <- base::c(
    base::paste(nameVariablePredict,"Lag1",sep = ""),
    base::paste(nameVariablePredict,"Lag2",sep = ""),
    base::paste(nameVariablePredict,"Lag3",sep = ""),
    base::paste(nameVariablePredict,"Lag4",sep = ""),
    base::paste(nameVariablePredict,"Lag5",sep = ""),
    "volLag1",
    "volLag2",
    "volLag3",
    "volLag4",
    "volLag5"
  )
  
  .linearModelEvalFirst <- base::paste("linearModelFited = lm(", nameVariablePredict , "~  ")
  .linearModelEvalEnd   <- ", data=databaseTrain)"
  
  .linearModelRMSEDataprice   <- base::c()
  .linearModelModelsFit       <- base::c()
  .linearModelPricePrediction <- base::c()
  
  .totalCombinaciones <- base::nrow(.combinacionesPosibles)
  
  # Recorremos todas las combinaciones posibles.
  for (i in base::c(1:.totalCombinaciones)) {
    
    eval <- ""
    totalVariables <- 0
    
    for ( variable in .variablesLag[.combinacionesPosibles[i,]==1]) {
      if (eval == "") {
        variable <- base::paste(" ", variable)
      } else {
        variable <- base::paste("+ ", variable)  
      }
      eval <- base::paste(eval, variable)
      totalVariables <- totalVariables + 1
    }
    
    if (eval!="") {
      
      linerModelEval <- base::paste(.linearModelEvalFirst, eval, .linearModelEvalEnd)
      
      # Se ejecuta una instancia de ajuste por eval.
      base::eval(base::parse(text=linerModelEval))
      predDataprice <- stats::predict(linearModelFited, databaseTest, interval = "prediction")
           
      # Guardamos el Modelo 
      .linearModelModelsFit[base::length(.linearModelModelsFit) + 1] <- linerModelEval
      
      .linearModelPricePrediction[base::length(.linearModelPricePrediction) + 1] <- predDataprice
      
    }
  }
  
  out <- base::data.frame(
    "model" = .linearModelModelsFit,
    "price" = .linearModelPricePrediction
  )
 
  return (out)
}
