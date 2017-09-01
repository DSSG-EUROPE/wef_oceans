library(plyr)
library(dplyr)
library(magrittr)
library(RPostgreSQL)

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

drv <- dbDriver("PostgreSQL")
 # creates a connection to the postgres database
 # note that "con" will be used later in each connection to the database
con <- dbConnect(drv, dbname = Sys.getenv('PGDATABASE'),
                 host = Sys.getenv('PGHOST')  , port = 5432,
                 user = Sys.getenv('PGUSER'), password = Sys.getenv('PGPASSWORD'))

