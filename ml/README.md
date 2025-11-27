# GeoJSON Baseline Regression

This script provides a simple **baseline regression model** for GeoJSON data.  
It:

- loads a GeoJSON file,
- converts `properties` + geometry (`longitude`, `latitude`) to a pandas DataFrame,
- preprocesses numeric and categorical features,
- trains a **Ridge regression** model,
- performs a **train / validation / test split**,
- prints basic metrics (RMSE, MAE).
