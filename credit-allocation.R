library(torch)
options(scipen = 999)

rnd_error <- 1.0 * (10^(-4))

## gibbs free energy of reaction
## reagents
gp1 <- torch_tensor(-1150, requires_grad = TRUE)
mp1 <- torch_tensor(1, requires_grad = TRUE)
gp2 <- torch_tensor(-300, requires_grad = TRUE)
mp2 <- torch_tensor(3, requires_grad = TRUE)
gp3 <- torch_tensor(0, requires_grad = TRUE)
mp3 <- torch_tensor(0, requires_grad = TRUE)

gr1 <- torch_tensor(-1420, requires_grad = TRUE)
mr1 <- torch_tensor(1, requires_grad = TRUE)
gr2 <- torch_tensor(-237, requires_grad = TRUE)
mr2 <- torch_tensor(2, requires_grad = TRUE)
gr3 <- torch_tensor(0, requires_grad = TRUE)
mr3 <- torch_tensor(0, requires_grad = TRUE)

n1 <- gp1 * mp1
n1$retain_grad()

n2 <- gp2 * mp2
n2$retain_grad()

n3 <- gp3 * mp3
n3$retain_grad()

n4 <- n1 + n2
n4$retain_grad()

## and for products
n5 <- n4 + n3
n5$retain_grad()

n6 <- gr1 * mr1
n6$retain_grad()

n7 <- gr2 * mr2
n7$retain_grad()

n8 <- gr3 * mr3
n8$retain_grad()

n9 <- n6 + n7
n9$retain_grad()

## ans for reagents
n10 <- n9 + n8
n10$retain_grad()

Y <- n5 - n10

## backward pass
Y$backward()

## results
results <- data.frame(nodes = c("n1","n2","n3","n4","n5",
                                "n6","n7","n8","np","n10","Y"),
                      frwd = c(as.numeric(n1),
                               as.numeric(n2),
                               as.numeric(n3),
                               as.numeric(n4),
                               as.numeric(n5),
                               as.numeric(n6),
                               as.numeric(n7),
                               as.numeric(n8),
                               as.numeric(n9),
                               as.numeric(n10),
                               as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               abs(as.numeric(n3$grad)),
                               abs(as.numeric(n4$grad)),
                               abs(as.numeric(n5$grad)),
                               abs(as.numeric(n6$grad)),
                               abs(as.numeric(n7$grad)),
                               abs(as.numeric(n8$grad)),
                               abs(as.numeric(n9$grad)),
                               abs(as.numeric(n10$grad)),
                               1.0),
                      error = rep(rnd_error, 11))

fc <- results$part %*% results$error
pc <- 2 * fc

## Calculating phi size

d <- torch_tensor(2.655, requires_grad = TRUE)
c2 <- torch_tensor(2.0, requires_grad = TRUE)
cn1 <- torch_tensor(-1.0, requires_grad = TRUE)

n1 <- log10(d)
n1$retain_grad()

n2 <- log10(c2)
n2$retain_grad()

n3 <- n1 / n2
n3$retain_grad()

Y <- n3 * cn1

## backward pass
Y$backward()

results <- data.frame(nodes = c("n1", "n2", "n3", "Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(n3),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               abs(as.numeric(n3$grad)),
                               1.0),
                      error = rep(rnd_error, 4))

fc <- results$part %*% results$error
pc <- 2 * fc


## penetration resistance (new method)

cg <- torch_tensor(9.8, requires_grad = TRUE)
h_weight <- torch_tensor(5.1, requires_grad = TRUE)
drop_dist_mm <- torch_tensor(310.0, requires_grad = TRUE)
pen_dist_cm <- torch_tensor(2.8, requires_grad = TRUE)
c1000 <- torch_tensor(1000.0, requires_grad = TRUE)
c100 <- torch_tensor(100.0, requires_grad = TRUE)
c2 <- torch_tensor(2.0, requires_grad = TRUE)

n1 <- drop_dist_mm / c1000
n1$retain_grad()

n2 <- pen_dist_cm / c100
n2$retain_grad()

n3 <- h_weight * cg
n3$retain_grad()

n4 <- n3 * n1
n4$retain_grad()

Y <- n4 / n2

## backward pass
Y$backward()

results <- data.frame(nodes = c("n1","n2","n3","n4","Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(n3),
                              as.numeric(n4),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               abs(as.numeric(n3$grad)),
                               abs(as.numeric(n4$grad)),
                               1.0),
                      error = rep(rnd_error, 5))

fc <- results$error %*% results$part
pc <- 2*fc

Y
fc
pc

## old method
n1 <- drop_dist_mm / c1000
n1$retain_grad()

n2 <- pen_dist_cm / c100
n2$retain_grad()

n3 <- cg * n1
n3$retain_grad()

n4 <- n3 * 2
n4$retain_grad()

n5 <- n4 * h_weight
n5$retain_grad()

n6 <- n5 / c2
n6$retain_grad()

Y <- n6 / n2

## backward
Y$backward()

results <- data.frame(nodes = c("n1","n2","n3","n4","n5","n6","Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(n3),
                              as.numeric(n4),
                              as.numeric(n5),
                              as.numeric(n6),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               abs(as.numeric(n3$grad)),
                               abs(as.numeric(n4$grad)),
                               abs(as.numeric(n5$grad)),
                               abs(as.numeric(n6$grad)),
                               1.0),
                      error = rep(rnd_error, 7))

fc <- results$part %*% results$error
pc <- 2*fc

Y
fc
pc

## Moisture content
dry <- torch_tensor(18.5, requires_grad = TRUE)
plastic <- torch_tensor(22.57, requires_grad = TRUE)
liquid <- torch_tensor(29.2, requires_grad = TRUE)
c100 <- torch_tensor(100.0 requires_grad = TRUE)

## plastic limit

n1 <- plastic - dry
n1$retain_grad()

n2 <- n1 / dry
n2$retain_grad()

Y <- n2 * c100

Y$backward()

results <- data.frame(nodes = c("n1","n2","Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               1.0),
                      error = rep(rnd_error, 3))

fc <- results$error %*% results$part
pc <- 2 * fc

Y
fc
pc

## liquid limit
n1 <- liquid - dry
n1$retain_grad()

n2 <- n1 / dry
n2$retain_grad()

Y <- n2 * c100

Y$backward()

results <- data.frame(nodes = c("n1","n2","Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               1.0),
                      error = rep(rnd_error, 3))

fc <- results$error %*% results$part
pc <- 2 * fc

Y
fc
pc

## plasticity index
n1 <- plastic - dry
n1$retain_grad()

n2 <- n1 / dry
n2$retain_grad()

n3 <- n2 * c100
n3$retain_grad()

n4 <- liquid - dry
n4$retain_grad()

n5 <- n4 / dry
n5$retain_grad()

n6 <- n5 * c100
n6$retain_grad()

Y <- n6 - n3

Y$backward()

results <- data.frame(nodes = c("n1","n2","n3","n4","n5","n6","Y"),
                      fwd = c(as.numeric(n1),
                              as.numeric(n2),
                              as.numeric(n3),
                              as.numeric(n4),
                              as.numeric(n5),
                              as.numeric(n6),
                              as.numeric(Y)),
                      part = c(abs(as.numeric(n1$grad)),
                               abs(as.numeric(n2$grad)),
                               abs(as.numeric(n3$grad)),
                               abs(as.numeric(n4$grad)),
                               abs(as.numeric(n5$grad)),
                               abs(as.numeric(n6$grad)),
                               1.0),
                      error = rep(rnd_error, 7))

fc <- results$part %*% results$error
pc <- 2*fc

Y
fc
pc
