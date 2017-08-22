###########################################################################
######################### PREPARE PACKAGES AND DATA #######################
###########################################################################
required_packages <- c("shiny", "rsconnect", "leaflet", "plyr", "dplyr", "htmltools", 
                       "shinythemes", "shinyBS", "DT", "ggplot2", "RPostgreSQL",
                       "leaflet", "magrittr")
#lapply(required_packages, install.packages)
lapply(required_packages, require, character.only=T)

#Load SQL connection object and query the whole table
source("data/dummy_data.R")
set.seed(123)
query <- "SELECT * FROM unique_vessel.aggregated_register_components"

#Subset data base and create new columns ranked by percentile in the empirical distribution
df_postgres <- dbGetQuery(con, query) %>%
	       dplyr::select(-mmsi) %>%
	       dplyr::mutate(last_longitude = as.character(last_longitude),
			     last_latitude = as.character(last_latitude)) %>%
	      #dplyr::filter(count_ais_position_yr > 100 & sat_imagery_count > 0) %>%
	       dplyr::mutate(mmsi_annon = as.character(round(runif(dim(.)[1], min=10000000, max = 999999999), 0))) %>%
	       dplyr::mutate_if(is.numeric, funs(cume_dist)) %>%
               dplyr::mutate(last_longitude = as.numeric(last_longitude),
                             last_latitude = as.numeric(last_latitude)) %>%
	       .[, c(15, 2, 3, 4, 12, 1, 5:11, 13, 14)]

#Define new names for table and make vectors for changes in style
num_names <- names(sapply(df_postgres, is.numeric)[sapply(df_postgres, is.numeric) == TRUE])
num_names_col <- names(sapply(df_postgres, is.numeric)[sapply(df_postgres, is.numeric) == TRUE]) %>%
	     setdiff(., c("last_latitude", "last_longitude")) 
new_names <- c('Vessel ID','Timestamp', 'Longitude', 'Latitude', 'Country', '# Messages','Fishing', 'Fishing (max.)',
	       'MPA presence', 'MPA presence (norm)', 'MPA presence (time)', 'EEZ presence','EEZ presence (norm)',
  	       'Satellite coverage', 'Time difference')


#Define color breaks for the DT table (green)
brks <- quantile(df_postgres[num_names], probs = seq(0, 1, by = 0.1), na.rm = TRUE)
clrs <- round(seq(255, 40, length.out = length(brks) + 1), 0) %>%
  paste0("rgb(", . ,  "," , "250 ,", . , ")")

#Let shiny print informative errors in logs and in the front-end 
options(shiny.sanitize.errors=FALSE)

########################################################################
################################### UI #################################
########################################################################
shinyApp(
  ui = navbarPage("Ranked list of IUU - DSSG",
                  theme = shinythemes::shinytheme("cosmo"),  # <--- Specify theme here
                  tabPanel("List",
			   includeCSS('www/style.css'),
		  fluidPage(
                    fluidRow(
                      column(2,
 			   h1("A tool to save our oceans"),
                           h4("This Ranked list uses Automatic Identification System Data (AIS) to identify suspicious behavior in the oceans from May of 2016 to June of 2017.", align="justify"),
			   helpText("This ranked list of unique vessels shows the last reported position and timestamp and a different set of components that comprises different types of ilegal activities overseas, and the likelihood of that vessel being fishing. You can select different components and sort the information according to your preferences", align="justify"),
			   HTML('<center><img src="dssg_logo_website.svg " height="250" width="300"/></center>')
			   ),
                      column(10,
                             DT::dataTableOutput("component_table"),
                             leafletOutput("mymap")
                             )
                             )
                  )),
                  tabPanel("About us - DSSG")
  ),
  server = function(input, output){
    
    ########################################################################
    ############################### DT TABLE ###############################
    ########################################################################
    
	
       output$component_table <- DT::renderDataTable(
		              datatable(df_postgres, colnames = new_names, filter='top', rownames = FALSE,
					options=list(scrollX=TRUE)) %>% 
			      formatRound(num_names, digits = 3) %>% 
			      formatDate("last_timestamp", method='toUTCString') %>%
			      formatStyle(num_names_col, backgroundColor = styleInterval(brks, clrs)),
			      options = list(pageLength=5, searchHighlight=TRUE, fixedColumns=TRUE)

   )
      
      ########################################################################
      ############################### LEAFLET MAP ############################
      ########################################################################
      
       output$mymap <- renderLeaflet({
      
         selection = input$component_table_rows_selected
	 subset_data <- df_postgres %>%
			.[selection, ] %>%
			dplyr::select(last_longitude, last_latitude) %>%
			dplyr::rename(longitude = last_longitude,
				       latitude = last_latitude)
	icons <- awesomeIcons(
		icon = 'ship',
		iconColor = 'black',
		library = 'fa'
	)      

         leaflet() %>%
           setView(lng = -36.278294, lat = 30.433400, zoom=2) %>% 
           addProviderTiles(providers$CartoDB.Positron) %>%
           #addCircleMarkers(data = subset_data)
	   addAwesomeMarkers(data = subset_data, icon=icons) 
       })
      

        # formatStyle(
        #     'days_fishing',
        #     background = styleColorBar(df_dummy$days_fishing, 'steelblue'),
        #     backgroundSize = '100% 90%',
        #     backgroundRepeat = 'no-repeat',
        #     backgroundPosition = 'center'
        #   )
 }
, options = list(height = 2000)) 

