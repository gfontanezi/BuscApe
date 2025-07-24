preco = input("Digite o preço do imóvel: R$")

if preco == "" or not preco.isdigit():
    preco = 150000
else:
    preco = int(preco)
    if preco <= 150000:
        preco = 150000

print(preco)
print(type(preco))