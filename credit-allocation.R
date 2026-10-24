library(torch)

rnd_error <- 1.0 * (10^(-4))
options(scipen = 999)

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
