###########################################################################
######################### PREPARE PACKAGES AND DATA #######################
###########################################################################

required_packages <- c("shiny", "rsconnect", "leaflet", "plyr", "dplyr", "htmltools", 
                       "shinythemes", "shinyBS", "DT", "ggplot2", "RPostgreSQL",
                       "leaflet")
#lapply(required_packages, install.packages)
lapply(required_packages, require, character.only=T)
source("data/dummy_data.R")
readRDS("data/dummy_data.rds")
brks <- quantile(df_dummy[5:length(df_dummy)], probs = seq(.05, .95, .05), na.rm = TRUE)
clrs <- round(seq(255, 40, length.out = length(brks) + 1), 0) %>%
  paste0("rgb(255,", ., ",", ., ")")


shinyApp(
  ui = navbarPage("Ranked list of IUU - DSSG",
                  theme = shinythemes::shinytheme("cosmo"),  # <--- Specify theme here
                  tabPanel("List",
                           h1("A Tool to save our oceans"),
                           h4("This Ranked list uses Automatic Identification System Data (AIS) to identify suspicious behavior
                             in the oceans from May of 2016 to June of 2017."),
                  fluidPage(
                    fluidRow(
                      column(2,
                             h2("List components weights"),
                             helpText("Select a weights for each of the components of the Risk score.
                               Please use values between 0 and 1. Being 0, the lowest weight and
                               1 the highest."),
                             # Decimal interval with step value
                             #helpPopup("title", "contents", placement = "right", trigger = "hover"),
                             sliderInput("trans", "Transhipment:", 
                                         min = 0, max = 1, value = 0.5, step= 0.1),
                             # HTML(paste0(
                             #     '<div class="form-group shiny-input-container">',
                             #     '<label class="control-label" for="decimal">Transshipment<a href="#" class="btn btn-mini"',
                             #     'data-toggle="popover" title=NULL data-content="Transshipment is the concurent navigation of two vessels (...)" 
                             #     data-animation="TRUE" data-placement="right"', 
                             #     'data-trigger="click"> <i class="glyphicon glyphicon-plus"></i></a>:</label> <input class="js-range-slider"',
                             #     'id="decimal" data-min="0" data-max="1" data-from="0.5" data-step="0.1" data-grid="true" data-grid-num="10" ',
                             #     'data-grid-snap="false" data-prettify-separator="," data-prettify-enabled="true" data-keyboard="true"',
                             #     'data-keyboard-step="10" data-data-type="number"/> </div>')),
                             sliderInput("eez", "EEZ Fishing:", 
                                         min = 0, max = 1, value = 0.5, step= 0.1),
                             sliderInput("ais", "AIS Signal loss:", 
                                         min = 0, max = 1, value = 0.5, step= 0.1)
                             ),
                      column(10,
                             DT::dataTableOutput("component_table"),
                             leafletOutput("mymap")
                             )
                             )

                    
                  )),
                  tabPanel("Activity Map"),
                  tabPanel("Modeling"),
                  tabPanel("About us - DSSG")
  ),
  server = function(input, output){
    
    ########################################################################
    ############################### DT TABLE ###############################
    ########################################################################
    
    df_dummy_score <- reactive({
      df_dummy %>%
        mutate(Score = input$trans * days_tranship + 
                 input$eez * days_eez +
                 input$ais * num_ais_loss) %>%
        arrange(., desc(Score))
    })
    
    output$component_table <- DT::renderDataTable(
      DT::datatable(df_dummy_score(), options = list(pageLength = 5)) %>%
        formatStyle(names(df_dummy_score()[5:length(df_dummy)]), backgroundColor = styleInterval(brks, clrs))
    )
      
      ########################################################################
      ############################### LEAFLET MAP ############################
      ########################################################################
      
       output$mymap <- renderLeaflet({
      
         selection = input$component_table_rows_selected
      
         leaflet() %>%
           addProviderTiles(providers$CartoDB.Positron) %>%
           addCircleMarkers(data = df_dummy[selection, c("lon", "lat")])
       })
      

        # formatStyle(
        #     'days_fishing',
        #     background = styleColorBar(df_dummy$days_fishing, 'steelblue'),
        #     backgroundSize = '100% 90%',
        #     backgroundRepeat = 'no-repeat',
        #     backgroundPosition = 'center'
        #   )
  }
, options = list(height = 1080))

# shinyUI(fluidPage(
# 
#   # Application title
#   titlePanel("Old Faithful Geyser Data"),
# 
#   # Sidebar with a slider input for number of bins
#   sidebarLayout(
#     sidebarPanel(
#       sliderInput("bins",
#                   "Number of bins:",
#                   min = 1,
#                   max = 50,
#                   value = 30)
#     ),
# 
#     # Show a plot of the generated distribution
#     mainPanel(
#       plotOutput("distPlot")
#     )
#   )
# ))
