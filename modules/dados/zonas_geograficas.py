import unidecode


def normalizar_lista(l):
    return [unidecode.unidecode(x).strip().lower() for x in l]


# Listas de zonas geográficas
zona_norte = ['Abolição', 'Acari', 'Água Santa', 'Alto da Boa Vista', 'Anchieta', 'Andaraí', 'Bancários',
              'Barros Filho', 'Benfica', 'Bento Ribeiro', 'Bonsucesso', 'Brás de Pina', 'Cachambi', 'Cacuia',
              'Caju', 'Campinho', 'Cascadura', 'Catumbi', 'Cavalcanti', 'Cidade Universitária', 'Cocotá',
              'Coelho Neto', 'Colégio', 'Complexo do Alemão', 'Cordovil', 'Costa Barros', 'Del Castilho',
              'Encantado', 'Engenheiro Leal', 'Engenho da Rainha', 'Engenho de Dentro', 'Engenho Novo', 'Estácio',
              'Ilha do Governador', 'Galeão', 'Grajaú', 'Guadalupe', 'Higienópolis', 'Honório Gurgel', 'Inhaúma',
              'Irajá', 'Jacaré', 'Jacarezinho', 'Jardim América', 'Jardim Carioca', 'Jardim Guanabara',
              'Lins de Vasconcelos', 'Madureira', 'Manguinhos', 'Maracanã', 'Maré', 'Marechal Hermes',
              'Mangueira', 'Maria da Graça', 'Méier', 'Moneró', 'Olaria', 'Oswaldo Cruz', 'Parada de Lucas',
              'Parque Anchieta', 'Parque Colúmbia', 'Pavuna', 'Penha', 'Penha Circular', 'Piedade', 'Pilares',
              'Pitangueiras', 'Portuguesa', 'Praça da Bandeira', 'Praia da Bandeira', 'Quintino Bocaiúva', 'Ramos',
              'Riachuelo', 'Ribeiro', 'Ricardo de Albuquerque', 'Rocha', 'Rocha Miranda', 'Rocha Neto', 'Sampaio',
              'Rio Comprido', 'Vasco da Gama', 'São Cristóvão', 'São Francisco Xavier', 'Tauá', 'Tijuca',
              'Todos os Santos', 'Tomás Coelho', 'Turiaçu', 'Vaz Lobo', 'Vicente de Carvalho', 'Vigário Geral',
              'Vila Isabel', 'Vila Kosmos', 'Vila da Penha', 'Vista Alegre', 'Vila Kosmos', 'Zumbi', 'freguesia (ilha)']

zona_oeste = ['Anil', 'Bangu', 'Barra da Tijuca', 'Barra de Guaratiba', 'Camorim', 'Campo dos Afonsos',
              'Campo Grande', 'Cidade de Deus', 'Cosmos', 'Curicica', 'Deodoro', 'Freguesia',
              'Gardênia Azul', 'Gericinó', 'Grumari', 'Guaratiba', 'Ilha de Guaratiba', 'Inhoaíba', 'Itanhangá',
              'Jabour', 'Jacarepaguá', 'Jardim Sulacap', 'Joá', 'Magalhães Bastos', 'Paciência', 'Padre Miguel',
              'Pechincha', 'Pedra de Guaratiba', 'Praça Seca', 'Realengo', 'Recreio dos Bandeirantes', 'Santa Cruz',
              'Santíssimo', 'Senador Camará', 'Senador Vasconcelos', 'Sepetiba', 'Tanque', 'Taquara',
              'Vargem Grande', 'Vargem Pequena', 'Vila Kennedy', 'Vila Militar', 'Vila Valqueire', 'Rio das Pedras']

zona_sul = ['Ipanema', 'Botafogo', 'Catete', 'Copacabana', 'Lagoa', 'Flamengo', 'Gávea', 'Humaitá',
            'Jardim Botânico', 'Laranjeiras', 'Leme', 'Urca', 'Vidigal', 'Cosme Velho', 'São Conrado',
            'Rocinha', 'Leblon', 'Santo Amaro']

baixada_fluminense = ['Nova Iguaçu', 'Duque de Caxias', 'Belford Roxo', 'São João de Meriti', 'Nilópolis',
                      'Mesquita', 'Magé', 'Queimados', 'Itaguaí', 'Japeri', 'Guapimirim', 'Paracambi', 'Seropédica',
                      'Tanguá']
bairros_centro = ['Gamboa', 'Centro do Rio', 'Centro', 'Lapa', 'Saúde', 'Cidade Nova', 'Santa Teresa', 'Estácio',
                  'Catumbi', 'Santo Cristo', 'Paquetá', 'Glória', 'Praça da República', 'Praça Mauá',
                  'Bairro de Fátima']

regiao_volta_redonda = ['Valença', 'Vassouras', 'Miguel Pereira', 'Paty do Alferes', 'Rio das Flores', 'Barra do Piraí',
                        'Piraí', 'Pinheiral', 'Volta Redonda', 'Barra Mansa', 'Resende', 'Itatiaia', 'Quatis',
                        'Porto Real', 'Rio Claro', 'Barra Mansa']

niteroi_sao_goncalo = ['Niterói', 'Icaraí', 'Santa Rosa', 'Fonseca', 'Barreto', 'Ingá', 'São Francisco',
                       'Piratininga', 'Itaipu', 'Várzea das Moças', 'Cubango', 'Cantagalo', 'Vital Brazil',
                       'São Domingos', 'Baldeador', 'Caramujo', 'Engenhoca', 'Santana', 'Pé Pequeno',
                       'Largo da Batalha', 'Matapaca', 'Ponta d\'Areia', 'São Lourenço', 'Sapê', 'Piratininga',
                       'Itacoatiara', 'Itaipu', 'Camboinhas', 'Maravista', 'Maria Paula', 'Santo Antônio',
                       'São Gonçalo', 'Alcântara', 'Mutondo', 'Neves', 'Porto da Pedra', 'Trindade', 'Zé Garoto',
                       'Boaçu',
                       'Itaboraí', 'Manilha']

regiao_serrana = ['Bom Jardim', 'Cantagalo', 'Carmo', 'Cordeiro', 'Duas Barras', 'Macuco', 'Nova Friburgo',
                  'Petrópolis', 'São José do Vale do Rio Preto', 'São Sebastião do Alto', 'Santa Maria Madalena',
                  'Sumidouro', 'Teresópolis', 'Trajano de Morais', 'Areal', 'São José do Vale do Rio Preto',
                  'Comendador Levy Gasparian', 'Paraiba do Sul', 'Sapucaia', 'Três Rios']

regiao_campos = ['Campos dos Goytacazes', 'Cardoso Moreira', 'São Fidélis', 'São Francisco de Itabapoana',
                 'Cardoso Moreira', 'São João da Barra', 'Bom Jesus do Itabapoana', 'Itaperuna', 'Laje do Muriaé',
                 'Natividade', 'Porciúncula', 'Sao Jose de Ubá', 'Varre-Sai', 'Cambuci', 'Italva', 'Itaocara',
                 'Miracema', 'Santo Antônio de Pádua']

regiao_dos_lagos = ['Cabo Frio', 'Arraial do Cabo', 'Araruama', 'Saquarema', 'Iguaba Grande',
                    'São Pedro da Aldeia', 'Maricá', 'Rio das Ostras', 'Armacao dos Buzios', 'Casimiro de Abreu',
                    'Conceição de Macabu', 'Quissamã', 'Macaé', 'Carapebus']

regiao_costa_verde = ['Angra dos Reis', 'Paraty', 'Mangaratiba', 'Itaguaí']

zona_oeste = normalizar_lista(zona_oeste)
zona_norte = normalizar_lista(zona_norte)
zona_sul = normalizar_lista(zona_sul)
baixada_fluminense = normalizar_lista(baixada_fluminense)
niteroi_sao_goncalo = normalizar_lista(niteroi_sao_goncalo)
regiao_serrana = normalizar_lista(regiao_serrana)
regiao_campos = normalizar_lista(regiao_campos)
regiao_dos_lagos = normalizar_lista(regiao_dos_lagos)
bairros_centro = normalizar_lista(bairros_centro)
regiao_volta_redonda = normalizar_lista(regiao_volta_redonda)
regiao_costa_verde = normalizar_lista(regiao_costa_verde)

ZONAS_GEOGRAFICAS = {
    "zona norte": zona_norte,
    "zona oeste": zona_oeste,
    "zona sul": zona_sul,
    "baixada fluminense": baixada_fluminense,
    "centro": bairros_centro,
    "niterói / são gonçalo": niteroi_sao_goncalo,
    "região serrana": regiao_serrana,
    "região dos lagos": regiao_dos_lagos,
    "região de campos": regiao_campos,
    "volta redonda e arredores": regiao_volta_redonda,
    "região costa verde": regiao_costa_verde
}
