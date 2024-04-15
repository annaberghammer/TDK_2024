setwd("C:/Users/bpank/OneDrive - Corvinus University of Budapest/Dokumentumok/LIFE/Egyetem/TDK/TDK 2.0")

library(readxl)
library(kohonen)
library(xlsx)

#########################################################################################################
### Data without text polarity

data <- read_xlsx(path = "data_final.xlsx")

# Remove unnecessarily columns from the dataset

data <- data[, !names(data) %in% c("General review polarity", "Positive/Negative characters’ ratio")]

# Convert the strings to factors
data$`Company name` <- as.factor(data$`Company name`)
data$`Short description` <- as.factor(data$`Short description`)
data$`Number of employees` <- as.factor(data$`Number of employees`)

# Ordering different types of variables into lists

som_input <- list(number_of_reviews=data$`Number of reviews`,
                  description=data$`Short description`,
                  number_of_employees=data$`Number of employees`,
                  overall_score=data$`Overall score`,
                  recommendation=data$Recommendation,
                  reviewer_data=as.matrix(data[, 7:15]),
                  professional_development=as.matrix(data[c("Provide training in the beginning",
                  "Professionally challenging", 
                  "Supporting trainings",
                  "High responsibility", 
                  "Varied, exciting",
                  "Opportunities for development and advancement")]),
                  work_and_workload=as.matrix(data[c("Stressful",
                                                     "Monotonous",
                                                     "Physically demanding",
                                                     "Hours and working hours",
                                                     "Bosses",
                                                     "Work-life balance")]),
                  benefits=as.matrix(data[c("Provide the working tools",
                                            "Flexible",
                                            "Cohesive team",
                                            "Salary and benefits",
                                            "Colleagues and company atmosphere")]),
                  work_environment=as.matrix(data[c("Work for good cause",
                                                    "Family friendly place",
                                                    "Environmentally friendly place",
                                                    "Contact",
                                                    "Working environment")]))

som_result <- supersom(som_input, somgrid(8,8,"hexagonal"), rlen = 10000)

# Data analysis

# Evolution of the objective function during training iterations (10000)
plot(som_result, type = "changes")

# Extract the training results
objective_function <- som_result$changes

# Create a data frame
training_data <- data.frame(iteration = iterations, objective_function = objective_function)

names(training_data)[names(training_data) == 'objective_function.number_of_reviews'] <- 'Number of reviews'
names(training_data)[names(training_data) == 'objective_function.description'] <- 'Description'
names(training_data)[names(training_data) == 'objective_function.number_of_employees'] <- 'Number of employees'
names(training_data)[names(training_data) == 'objective_function.overall_score'] <- 'Overall score'
names(training_data)[names(training_data) == 'objective_function.recommendation'] <- 'Recommendation'
names(training_data)[names(training_data) == 'objective_function.reviewer_data'] <- 'Reviewer data'
names(training_data)[names(training_data) == 'objective_function.professional_development'] <- 'Professional development'
names(training_data)[names(training_data) == 'objective_function.work_and_workload'] <- 'Work and workload'
names(training_data)[names(training_data) == 'objective_function.benefits'] <- 'Benefits'
names(training_data)[names(training_data) == 'objective_function.work_environment'] <- 'Work environment'

training_data <- training_data[, c(1, 2, 3, 6, 7, 8, 9, 10, 11, 4, 5)]

training_data[2] <- training_data[2]
training_data[3] <- training_data[3] * 100 
training_data[4] <- training_data[4] * 2.5
training_data[5] <- training_data[5] * 2
training_data[6] <- training_data[6] * 100
training_data[7] <- training_data[7] * 100
training_data[8] <- training_data[8] * 100
training_data[9] <- training_data[9] * 100
training_data[10] <- training_data[10] * 100
training_data[11] <- training_data[11] * 200


# Plotting the training process using ggplot
d <- melt(training_data, id.vars = "iteration")

# Colors
rhg_cols <- c("#000000","#556670","#dddddd","#aaaaaa","#28666E",
              "#7C9885","#B6C5CC","#8E9CA3","#1a1b41","#033F63")

ggplot(d, aes(x = iteration, y = value, col = variable)) +
  geom_line() +
  labs(x = "Iteration", y = "Relative distance to closest unit", 
       title = "Training process") +
  scale_colour_manual(values = rhg_cols)

# Removing recommendation from the lists of variables

som_input2 <- list(number_of_reviews=data$`Number of reviews`,
                  description=data$`Short description`,
                  number_of_employees=data$`Number of employees`,
                  reviewer_data=as.matrix(data[, 7:15]),
                  professional_development=as.matrix(data[c("Provide training in the beginning",
                                                            "Professionally challenging", 
                                                            "Supporting trainings",
                                                            "High responsibility", 
                                                            "Varied, exciting",
                                                            "Opportunities for development and advancement")]),
                  work_and_workload=as.matrix(data[c("Stressful",
                                                     "Monotonous",
                                                     "Physically demanding",
                                                     "Hours and working hours",
                                                     "Bosses",
                                                     "Work-life balance")]),
                  benefits=as.matrix(data[c("Provide the working tools",
                                            "Flexible",
                                            "Cohesive team",
                                            "Salary and benefits",
                                            "Colleagues and company atmosphere")]),
                  work_environment=as.matrix(data[c("Work for good cause",
                                                    "Family friendly place",
                                                    "Environmentally friendly place",
                                                    "Contact",
                                                    "Working environment")]))

som_result2 <- supersom(som_input2, somgrid(8,8,"hexagonal"), rlen = 10000)

plot(som_result2, type = "changes")

objective_function2 <- som_result2$changes

training_data2 <- data.frame(iteration = iterations, objective_function = objective_function2)

names(training_data2)[names(training_data2) == 'objective_function.number_of_reviews'] <- 'Number of reviews'
names(training_data2)[names(training_data2) == 'objective_function.description'] <- 'Description'
names(training_data2)[names(training_data2) == 'objective_function.number_of_employees'] <- 'Number of employees'
names(training_data2)[names(training_data2) == 'objective_function.reviewer_data'] <- 'Reviewer data'
names(training_data2)[names(training_data2) == 'objective_function.professional_development'] <- 'Professional development'
names(training_data2)[names(training_data2) == 'objective_function.work_and_workload'] <- 'Work and workload'
names(training_data2)[names(training_data2) == 'objective_function.benefits'] <- 'Benefits'
names(training_data2)[names(training_data2) == 'objective_function.work_environment'] <- 'Work environment'

training_data2[2] <- training_data2[2]
training_data2[3] <- training_data2[3] * 100 
training_data2[4] <- training_data2[4] * 2.5
training_data2[5] <- training_data2[5] * 2
training_data2[6] <- training_data2[6] * 100
training_data2[7] <- training_data2[7] * 100
training_data2[8] <- training_data2[8] * 100
training_data2[9] <- training_data2[9] * 100

# Plotting the training process using ggplot
d2 <- melt(training_data2, id.vars = "iteration")

# Colors
rhg_cols <- c("#000000","#556670","#dddddd","#aaaaaa","#28666E",
              "#7C9885","#B6C5CC","#8E9CA3","#1a1b41","#033F63")

ggplot(d2, aes(x = iteration, y = value, col = variable)) +
  geom_line() +
  labs(x = "Iteration", y = "Relative distance to closest unit", 
       title = "Training process") +
  scale_colour_manual(values = rhg_cols)

# The profile of each type of variable in the reduced dimnesion space

plot(som_result2, type = "codes") 

# Frequencies
plot(som_result2, type = "counts", pchs = 20,  main = "Number of employers per cluster", labels = som_result2$unit.classif)

# Average distances to nearest neighbours - smaller for better
plot(som_result, type = "quality", pchs = 20,  main = "Average distances from the nearest neighbours")

som_result2_data <- as.data.frame(som_result2$data)
som_result2_data$cluster <- som_result2$unit.classif

# Hierarchical clustering

library(tidyverse)

# The values of 8*8=64 small-dimensional objects according to the original variables
codes_tibble <- tibble(layers = names(som_result2$codes), codes = som_result2$codes) %>%
  mutate(codes = purrr::map(codes, as_tibble)) %>%
  spread(key = layers, value = codes) %>%
  apply(1, bind_cols) %>%
  .[[1]] %>%
  as_tibble()

# Distance matrix of the low-dimensional (64 objects) table (euclidean)
distances = dist(codes_tibble) %>%
  as.matrix()

# Creation of dendogram
dendogram <- hclust(as.dist(distances))

# Optimal cluster number based on dendogram
plot(dendogram)
percentage <- 0.27
abline(h = max(dendogram$height)*percentage, col = 'red')

# Analyze outlier data

data_cluster1 <- som_result2_data[som_result2_data$cluster == 1, ]
data_cluster9 <- som_result2_data[som_result2_data$cluster == 9, ]

# Save cluster membership
cluster <- cutree(dendogram, h = max(dendogram$height)*percentage)

# Colour palette for clusters
library(RColorBrewer)

n <- length(unique(cluster))
qual_col_pals <- brewer.pal.info[brewer.pal.info$category == 'qual',]
color_vector <- unlist(mapply(brewer.pal, qual_col_pals$maxcolors, rownames(qual_col_pals)))

# Figures coloured by cluster membership
plot(som_result2, type="mapping", bgcol = color_vector[cluster], main = "Clusters") 
plot(som_result2, type="codes", bgcol = color_vector[cluster])

#########################################################################################################

# Data with textual reviews

data_text <- read_xlsx(path = "data_final.xlsx")

# Remove empty rows from the dataset

data_text <- na.omit(data_text)

# Convert the strings to factors
data_text$`Company name` <- as.factor(data_text$`Company name`)
data_text$`Short description` <- as.factor(data_text$`Short description`)
data_text$`Number of employees` <- as.factor(data_text$`Number of employees`)

# Ordering different types of variables into lists

som_input_text <- list(number_of_reviews=data_text$`Number of reviews`,
                  description=data_text$`Short description`,
                  number_of_employees=data_text$`Number of employees`,
                  reviewer_data=as.matrix(data_text[, 7:15]),
                  professional_development=as.matrix(data_text[c("Provide training in the beginning",
                                                            "Professionally challenging", 
                                                            "Supporting trainings",
                                                            "High responsibility", 
                                                            "Varied, exciting",
                                                            "Opportunities for development and advancement")]),
                  work_and_workload=as.matrix(data_text[c("Stressful",
                                                     "Monotonous",
                                                     "Physically demanding",
                                                     "Hours and working hours",
                                                     "Bosses",
                                                     "Work-life balance")]),
                  benefits=as.matrix(data_text[c("Provide the working tools",
                                            "Flexible",
                                            "Cohesive team",
                                            "Salary and benefits",
                                            "Colleagues and company atmosphere")]),
                  work_environment=as.matrix(data_text[c("Work for good cause",
                                                    "Family friendly place",
                                                    "Environmentally friendly place",
                                                    "Contact",
                                                    "Working environment")]),
                  polarity=as.matrix(data_text[c("General review polarity", 
                                            "Positive/Negative characters’ ratio")]))

som_result_text <- supersom(som_input_text, somgrid(8,8,"hexagonal"), rlen = 10000)

objective_function3 <- som_result_text$changes

training_data3 <- data.frame(iteration = iterations, objective_function = objective_function3)

names(training_data3)[names(training_data3) == 'objective_function.number_of_reviews'] <- 'Number of reviews'
names(training_data3)[names(training_data3) == 'objective_function.description'] <- 'Description'
names(training_data3)[names(training_data3) == 'objective_function.number_of_employees'] <- 'Number of employees'
names(training_data3)[names(training_data3) == 'objective_function.overall_score'] <- 'Overall score'
names(training_data3)[names(training_data3) == 'objective_function.recommendation'] <- 'Recommendation'
names(training_data3)[names(training_data3) == 'objective_function.reviewer_data'] <- 'Reviewer data'
names(training_data3)[names(training_data3) == 'objective_function.professional_development'] <- 'Professional development'
names(training_data3)[names(training_data3) == 'objective_function.work_and_workload'] <- 'Work and workload'
names(training_data3)[names(training_data3) == 'objective_function.benefits'] <- 'Benefits'
names(training_data3)[names(training_data3) == 'objective_function.work_environment'] <- 'Work environment'
names(training_data3)[names(training_data3) == 'objective_function.polarity'] <- 'Polarity'

training_data3[2] <- training_data3[2]
training_data3[3] <- training_data3[3] * 100 
training_data3[4] <- training_data3[4] * 2.5
training_data3[5] <- training_data3[5] * 2
training_data3[6] <- training_data3[6] * 100
training_data3[7] <- training_data3[7] * 100
training_data3[8] <- training_data3[8] * 100
training_data3[9] <- training_data3[9] * 100
training_data3[10] <- training_data3[10] * 100


# Plotting the training process using ggplot
d3 <- melt(training_data3, id.vars = "iteration")

# Colors
rhg_cols <- c("#000000","#556670","#dddddd","#aaaaaa","#28666E",
              "#7C9885","#B6C5CC","#8E9CA3","#1a1b41","#033F63")

ggplot(d3, aes(x = iteration, y = value, col = variable)) +
  geom_line() +
  labs(x = "Iteration", y = "Relative distance to closest unit", 
       title = "Training process") +
  scale_colour_manual(values = rhg_cols)

# Data analysis

# Evolution of the objective function during training iterations (10000)
plot(som_result_text, type = "changes")

# The profile of each type of variable in the reduced dimnesion space

plot(som_result_text, type = "codes") 

# Frequencies
plot(som_result_text, type = "counts", pchs = 20,  main = "Number of employers per cluster")

# Average distances to nearest neighbours - smaller for better
plot(som_result_text, type = "quality", pchs = 20,  main = "Average distances from the nearest neighbours")

som_result_text_data <- as.data.frame(som_result_text$data)
som_result_text_data$cluster <- som_result_text$unit.classif

# Hierarchical clustering

library(tidyverse)

# The values of 8*8=64 small-dimensional objects according to the original variables
codes_tibble_text <- tibble(layers = names(som_result_text$codes), codes = som_result_text$codes) %>%
  mutate(codes = purrr::map(codes, as_tibble)) %>%
  spread(key = layers, value = codes) %>%
  apply(1, bind_cols) %>%
  .[[1]] %>%
  as_tibble()

# Distance matrix of the low-dimensional (64 objects) table (euclidean)
distances_text = dist(codes_tibble_text) %>%
  as.matrix()

# Creation of dendogram
dendogram_text <- hclust(as.dist(distances_text))

# Optimal cluster number based on dendogram
plot(dendogram_text)
percentage_text <- 0.25
abline(h = max(dendogram_text$height)*percentage_text, col = 'red')

# Analyze outlier data

data_text_cluster8 <- som_result_text_data[som_result_text_data$cluster == 8, ]
data_text_cluster16 <- som_result_text_data[som_result_text_data$cluster == 16, ]
data_text_cluster23 <- som_result_text_data[som_result_text_data$cluster == 23, ]

# Save cluster membership
cluster_text <- cutree(dendogram_text, h = max(dendogram_text$height)*percentage_text)

# Colour palette for clusters
library(RColorBrewer)

n_text <- length(unique(cluster_text))
qual_col_pals_text <- brewer.pal.info[brewer.pal.info$category == 'qual',]
color_vector_text <- unlist(mapply(brewer.pal, qual_col_pals$maxcolors, rownames(qual_col_pals)))

# Figures coloured by cluster membership
plot(som_result_text, type="mapping", bgcol = color_vector[cluster_text], main = "Clusters") 
plot(som_result_text, type="codes", bgcol = color_vector[cluster_text])

#########################################################################################################

# Adding cluster membership for database

data_all <- read_xlsx(path = "data_final.xlsx")
data_all$cluster <- som_result2_data$cluster
data_text$cluster <- som_result_text_data$cluster

data_filtered <- na.omit(data_all)

write.xlsx(list("Without textual review" = data_filtered, 
                "With textual review" = data_text, 
                "Cluster - without t. review" = cluster,
                "Cluster - with t. review" = cluster_text),
           'Cluster memberships.xlsx')

#########################################################################################################

# Entering cluster membership in the original, high-dimensional table
cluster_to_grid <- as.data.frame(cluster)
cluster_to_grid$grid_member <- rownames(cluster_to_grid)

clustered_data <- cbind(data, som_result2$unit.classif)
colnames(clustered_data)[39] <- "grid_member"
clustered_data <- merge(clustered_data, cluster_to_grid, by = "grid_member")

# Check
barplot(table(clustered_data$cluster.y))

# Box-plot of the clusters in the original large dimension table
plotdata <- subset(clustered_data, select = c("cluster.y",
                                              "Number of employees",
                                              "Provide the working tools",
                                              "Provide training in the beginning",
                                              "Stressful",
                                              "Work for good cause",
                                              "Flexible",
                                              "Family friendly place",
                                              "Professionally challenging",
                                              "Monotonous",
                                              "Environmentally friendly place",
                                              "Supporting trainings",
                                              "High responsibility",
                                              "Physically demanding",
                                              "Cohesive team",
                                              "Varied, exciting",
                                              "Salary and benefits",
                                              "Hours and working hours",
                                              "Bosses",
                                              "Opportunities for development and advancement",
                                              "Work-life balance",
                                              "Colleagues and company atmosphere",
                                              "Contact",
                                              "Working environment"
                                              ))

plotdata <- reshape2::melt(plotdata, id.vars = c("cluster.y", "Number of employees"))

ggplot(plotdata, aes(x = as.factor(variable), y = value)) +
  geom_boxplot(outlier.shape = NA) +
  facet_wrap(~cluster.y) +
  theme(axis.text.x=element_text(angle = 90,hjust = 1,vjust = 0.5), 
        axis.title = element_blank())
