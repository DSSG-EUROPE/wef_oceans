library(plyr)
library(dplyr)
library(magrittr)
library(RPostgreSQL)
#########################################################################
########################## DATA DUMMY CREATION ##########################
#########################################################################
set.seed(1234)
latemail <- function(N, st="2016/05/01", et="2017/06/15"){
  st <- as.POSIXct(as.Date(st, tz = 'GMT'))
  et <- as.POSIXct(as.Date(et, tz = 'GMT'))
  dt <- as.numeric(difftime(et,st,unit="sec"))
  ev <- sort(runif(N, 0, dt))
  rt <- st + ev
}

create_dummy_ais <- function(number_rows)
df_dummy = data.frame(matrix(runif(10000, min=1, max=100), nrow=number_rows, ncol = 4, byrow = T)) %>%
  set_colnames(c("days_fishing", "days_tranship", "days_eez", "num_ais_loss")) %>%
  mutate(., lat = runif(number_rows, min=-90, max=90),
         lon = runif(number_rows, min=-180, max=180),
         mmsi = runif(number_rows, min=10000000, max = 999999999),
         timestamp = latemail(number_rows)
  ) %>%
  dplyr::select(., mmsi, timestamp, lon, lat, days_fishing, days_tranship, days_eez, num_ais_loss)

df_dummy <- create_dummy_ais(10000)
saveRDS(df_dummy, 'dummy_data.rds')


#########################################################################
############################ BOOTSTRAP POP-UP  ##########################
#########################################################################


helpPopup <- function(title, content,
                      placement=c('right', 'top', 'left', 'bottom'),
                      trigger=c('click', 'hover', 'focus', 'manual')) {
  tagList(
    singleton(
      tags$head(
        tags$script("$(function() { $(\"[data-toggle='popover']\").popover(); })")
      )
    ),
    tags$a(
      href = "#", class = "btn btn-mini", `data-toggle` = "popover",
      title = title, `data-content` = content, `data-animation` = TRUE,
      `data-placement` = match.arg(placement, several.ok=TRUE)[1],
      `data-trigger` = match.arg(trigger, several.ok=TRUE)[1],
      icon("", lib = "glyphicon") 
      
    )
  )
}


#########################################################################
########################## DATA CONNECTION TO  ##########################
############################# POSTGRESQL ################################
#########################################################################
 # create a connection
 # save the password that we can "hide" it as best as we can by collapsing it
# pw <- {
#   "new_user_password"
# }
 
drv <- dbDriver("PostgreSQL")
 # creates a connection to the postgres database
 # note that "con" will be used later in each connection to the database
con <- dbConnect(drv, dbname = Sys.getenv('PGDATABASE'),
                 host = Sys.getenv('PGHOST')  , port = 5432,
                 user = Sys.getenv('PGUSER'), password = Sys.getenv('PGPASSWORD'))
# rm(pw) # removes the password
 
# # check for the cartable
# dbExistsTable(con, "cartable")
