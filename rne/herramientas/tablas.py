"""Tablas del RNE reconstruidas a mano (el texto del PDF pierde las columnas).

Clave: (norma, comienzo del título del cuadro). Cada fila es un texto con celdas separadas por «|».
  ^   la celda une con la de arriba (rowspan)      <   la celda une con la de la izquierda (colspan)
  #…  fila de grupo que ocupa todo el ancho
h = filas de encabezado, r = filas, n = notas, cap = subtítulo, end = primera línea del texto que sigue a la tabla
(si falta, la tabla consume las líneas que detectó el lector automático).
"""
import re

T = {}
T[('A010', 'Cuadro N° 01')] = dict(
    h=['Edificación|Vehículo de emergencia|<|<', '^|Altura mínima|Ancho mínimo|Largo mínimo'],
    r=['Vivienda, oficinas y hospedaje|3.00 m|2.50 m|5.00 m',
       'Edificaciones comerciales, industriales, salud, educación, servicios comunales, recreación y deportes, transportes y comunicaciones|4.50 m|3.25 m|12.00 m'])
T[('A010', 'Cuadro N° 02')] = dict(
    h=['Tipo de pasajes y circulaciones|Ancho mínimo'],
    r=['Interior de viviendas|0.90 m', 'Pasajes que sirven de acceso hasta a dos viviendas|1.00 m',
       'Pasajes que sirven de acceso hasta a cuatro viviendas|1.20 m', 'Áreas de trabajo interiores en oficinas|0.90 m',
       'Pasajes de servicio (que sirven de acceso a depósitos, a cuartos técnicos, a servicios higiénicos, a ambientes auxiliares, entre otros, que permita el normal desplazamiento de equipo previsto para mantenimiento, reparación o recambio de equipos)|0.90 m',
       'Establecimiento de hospedaje|1.20 m',
       'Locales comerciales, entre góndolas o anaqueles de consumo cotidiano, y para productos especializados cuando las dimensiones del producto lo permitan|1.20 m',
       'Locales de salud|1.80 m', 'Locales educativos|1.20 m'])
for k, v in (('03', ('2.70', '2.50', '2.40', '5.00', '2.40', '5.40', ' (***)')), ('04', ('3.00', '2.60', '2.50', '5.00', '2.50', '6.00', ''))):
    T[('A010', 'Cuadro N° ' + k)] = dict(
        h=['Descripción|Ancho de cajón|Largo de cajón|Altura libre'],
        r=[f'Estacionamiento individual|{v[0]} m|{v[3]} m (*)|2.10 m{v[6]}', f'02 estacionamientos contiguos|{v[1]} m|^|^',
           f'03 o más estacionamientos contiguos|{v[2]} m|^|^', f'Estacionamiento en paralelo|{v[4]} m|{v[5]} m (**)|2.10 m'],
        n=['(*) El cajón puede desarrollarse en una pendiente de hasta 6%.'])
T[('A010', 'Cuadro N° 05')] = dict(h=['Medida|Mínimo'], r=['Ancho|0.75 m cada uno', 'Largo|2.00 m cada uno'])
T[('A010', 'Cuadro N° 06')] = dict(h=['Medida|Mínimo'], r=['Ancho|1.50 m cada uno', 'Largo|2.50 m cada uno'])

T[('A020', 'Cuadro Nº 01')] = dict(
    h=['Clasificación|Tipología'],
    r=['Edificación para grupos familiares|Vivienda unifamiliar', '^|Vivienda bifamiliar', '^|Quinta', '^|Vivienda taller',
       '^|Vivienda multifamiliar', '^|Conjunto habitacional / residencial', 'Edificación para grupos de individuos|Vivienda de uso colectivo'])
T[('A020', 'Cuadro Nº 02')] = dict(
    h=['Vivienda|Número de personas'],
    r=['De un dormitorio|2', 'De dos dormitorios|3', 'De tres dormitorios|4',
       'Con más de tres dormitorios, para vivienda multifamiliar y conjunto residencial|1 persona adicional por dormitorio',
       'Vivienda de uso colectivo|1 persona por dormitorio'])
T[('A020', 'Cuadro Nº 03')] = dict(
    h=['Ambientes|Distancia mínima'], r=['Dormitorio, sala y comedor|2.00 m', 'Cocina y patios de servicios techados|1.80 m'])
_pz = []
for tramo, vals in (('Primeros 18.00 m', (30, 25, 35, 30)), ('Siguientes 18.00 m (de 19.00 a 36.00 m)', (15, 13, 25, 16)),
                    ('Siguientes 18.00 m (de 37.00 a 54.00 m)', (10, 10, 15, 13)), ('Siguientes 18.00 m (de 55.00 a 72.00 m)', (10, 10, 15, 13))):
    _pz += [f'{tramo}|A|1 y 2 lados|{vals[0]}%', f'^|B|^|{vals[1]}%', f'^|A|3 y 4 lados|{vals[2]}%', f'^|B|^|{vals[3]}%']
T[('A020', 'Cuadro Nº 04')] = dict(
    h=['Altura de la edificación|Ambientes a iluminar y ventilar|Nº de lados del pozo|Distancia perpendicular, respecto a la altura de la edificación más baja opuesta'],
    r=_pz, n=['A = dormitorios, salas y comedores.', 'B = cocinas y patios techados.'], end='Notas:')
T[('A020', 'Cuadro Nº 05')] = dict(
    h=['Ambientes|Distancia perpendicular, respecto a la altura de la edificación más baja opuesta|Distancia mínima|Distancia máxima exigible'],
    r=['A|30%|5.00 m|20.00 m', 'B|25%|4.00 m|15.00 m'],
    n=['A = dormitorios, salas y comedores.', 'B = cocinas y patios techados.'], end='Notas:')
T[('A020', 'Cuadro Nº 06')] = dict(
    h=['Tipo de vano|Ancho mínimo'],
    r=['Acceso principal a una unidad de vivienda|0.90 m', 'Acceso a ambientes de descanso (dormir), reunión (estar), alimentación (cocinar y comer)|0.80 m',
       'Acceso a ambientes de aseo y servicios (baños)|0.70 m', 'Acceso principal a una vivienda multifamiliar, de uso colectivo o conjunto residencial|1.20 m'])
T[('A020', 'Cuadro Nº 07')] = dict(
    h=['Tipo|Ancho mínimo'],
    r=['Interiores de las viviendas|0.90 m', 'De acceso hasta 2 viviendas|1.00 m', 'De acceso hasta 4 viviendas|1.20 m', 'Áreas comunes de acceso a las viviendas|1.20 m'])
T[('A020', 'Cuadro Nº 08')] = dict(
    h=['Vivienda|Aparatos'], r=['Hasta 25.00 m²|1 inodoro, 1 ducha y 1 lavadero', 'Más de 25.00 m²|1 inodoro, 1 lavatorio, 1 ducha y 1 lavadero'])
_inc = []
for tip, filas in (('Unifamiliar', ['-|-|-|-|-|-|-|-|-|-|-|-|-']), ('Bifamiliar', ['-|1|-|-|-|-|-|-|11|12|13|-|-']),
                   ('Quinta', ['-|1|-|-|6|-|-|-|-|-|-|-|-']), ('Vivienda taller', ['-|-|2|-|6|-|-|-|11|12|-|-|-'])):
    _inc += [tip + '|' + filas[0]]
for tip in ('Multifamiliar y/o conjunto residencial', 'De uso colectivo'):
    _inc += [f'{tip}|Hasta 15 m|1|2|-|6|-|9|-|11|12|13|14|15', '^|Más de 15 hasta 30 m|1|3|4|7|8|9|-|-|12|13|14|15',
             '^|Más de 30 hasta 60 m|1|3|5|7|8|9|-|-|12|-|14|15', '^|Más de 60 m|1|3|5|7|8|-|10|-|12|-|14|15']
T[('A020', 'Cuadro Nº 09')] = dict(
    h=['Tipología de vivienda|Altura|Señalética / iluminación de emergencia|Detectores de humo / alarma de humo|Central de alarma contra incendios|Extintores|Red de agua contra incendios / bomba contraincendios|<|Rociadores|Escalera protegida (cualquiera de estas opciones)|<|<|<|<'],
    r=_inc, n=['Los números remiten a las notas que siguen al cuadro; «-» = no se exige.'], end='Notas:')

T[('A030', 'Tabla N° 1')] = dict(
    h=['Clase|Categoría|Requisitos técnicos mínimos'],
    r=['Hotel|Uno a cinco estrellas|Ver Anexo 1', 'Apart-hotel|Tres a cinco estrellas|Ver Anexo 2', 'Hostal|Una a tres estrellas|Ver Anexo 3', 'Albergue|-|Ver Anexo 4'])

T[('A040', 'Cuadro N° 1')] = dict(
    h=['Educación|Tipo de local'],
    r=['Educación Básica|Educación Básica Regular (EBR)', '^|Educación Básica Alternativa (EBA)', '^|Educación Básica Especial (EBE)',
       'Educación Superior|Universidades', '^|Institutos de Educación Superior', '^|Escuelas de Educación Superior', '^|Escuelas de postgrado',
       'Otras formas de atención educativa|Institutos o Centros de Idiomas (*)', '^|Centros de Educación Técnico Productiva (CETPRO)',
       '^|Centros de Educación Comunitaria', '^|Centros preuniversitarios (*)',
       '^|Otros de naturaleza semejante donde se desarrollen actividades de capacitación y educación'])
T[('A040', 'Cuadro N° 2')] = dict(
    h=['Nº|Ambiente'],
    r=['1|Aulas', '2|Sala de Usos Múltiples (SUM)', '3|Talleres', '4|Laboratorios', '5|Sala de cómputo / Sala de idiomas',
       '6|Circulaciones / Vestíbulos y similar', '7|Servicios higiénicos (SS.HH.) / Vestuarios', '8|Bibliotecas', '9|Otros'],
    end='La iluminación natural')
T[('A040', 'Cuadro N° 3')] = dict(
    h=['Principales ambientes|Coeficiente de ocupantes'],
    r=['Auditorios|Según el número de asientos', 'Salas de Usos Múltiples|1.0 m² por persona', 'Aulas|1.5 m² por persona',
       'Talleres y Laboratorios|3.0 m² por persona', 'Bibliotecas|2.0 m² por persona', 'Oficinas|9.5 m² por persona'])
T[('A040', 'Cuadro N° 4')] = dict(
    cap='Educación Básica Regular (EBR)',
    h=['Aparatos|Inicial (*)|<|Primaria / Secundaria|<', '^|Niños|Niñas|Hombres|Mujeres'],
    r=['Inodoro|1 c/25|1 c/25|1 c/60|1 c/30', 'Lavatorios (**)|1 c/25|1 c/25|1 c/30|1 c/30', 'Urinario (**)|1 c/25|-|1 c/60|-'],
    end='(*) Para el Ciclo')
_lav = '(*) Los lavatorios y urinarios pueden sustituirse por aparatos de mampostería corridos recubiertos de material vidriado, a razón de 0.60 m por posición.'
for k, cap, extra in (('5', 'Educación Básica Alternativa (EBA)', []),
                      ('6', 'Educación Básica Especial (EBE)', ['Para los SS.HH. anexos al aula o sala educativa, se debe considerar las disposiciones normativas del MINEDU.']),
                      ('7', 'Educación Superior', []), ('8', 'Otras formas de atención educativa', [])):
    T[('A040', 'Cuadro N° ' + k)] = dict(cap=cap, h=['Aparatos|Hombres|Mujeres'],
        r=['Inodoro|1 c/60|1 c/30', 'Lavatorios (*)|1 c/30|1 c/30', 'Urinario (*)|1 c/60|-'], n=[_lav] + extra)

T[('A070', 'Cuadro N° 1')] = dict(
    h=['Disposición|Sector'],
    r=['Establecimientos de venta de combustible y/o energía eléctrica|Ministerio de Energía y Minas',
       'Establecimientos de hospedaje y restaurantes|Ministerio de Comercio Exterior y Turismo',
       'Reglamento sanitario para establecimientos de expendio de comidas y bebidas|Ministerio de Salud',
       'Mercados de abastos, minoristas y mayoristas|Ministerio de la Producción'])
T[('A070', 'Cuadro N° 2')] = dict(
    h=['Tipo|Clasificación|Servicio'],
    r=['Locales comerciales individuales|Tienda independiente|',
       '^|Locales de expendio de comidas y bebidas|Restaurante', '^|^|Cafetería', '^|^|Local de comida rápida', '^|^|Local de venta de comidas al paso',
       '^|Locales de expendio de combustibles y/o de energía eléctrica|Establecimiento de venta de combustibles (estación de servicio, grifo, gasocentro) y/o de energía eléctrica para vehículos',
       '^|Locales bancarios y de intermediación financiera|',
       '^|Locales de entretenimiento y/o recreo|Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)',
       '^|Locales de servicios personales|Spa, baño turco, sauna, baño de vapor, barbería y/o salón de belleza', '^|^|Gimnasio, fisicoculturismo',
       '^|Tienda por departamentos|', '^|Tienda de autoservicio|Supermercado', '^|^|Tienda de mejoramiento del hogar', '^|^|Otras tiendas de autoservicio',
       '^|Locales de servicios para vehículos|Local de estacionamiento de vehículos', '^|^|Local de venta, mantenimiento y/o limpieza de vehículos',
       'Locales comerciales agrupados|Mercado de abastos|Mercado de abastos mayorista', '^|^|Mercado de abastos minorista',
       '^|Galería comercial|', '^|Centro comercial|', '^|Galería ferial|'],
    end='Los casos no expresamente')
_occ = [('#Tienda independiente', ''), ('Tienda independiente en primer piso (nivel de acceso)', '2.8'), ('Tienda independiente en segundo piso', '5.6'),
        ('Tienda independiente interconectada de dos niveles', '3.7'), ('#Locales de expendio de comidas y bebidas', ''),
        ('Restaurante, cafetería (cocina)', '9.3'), ('Restaurante, cafetería (área de mesas)', '1.5'), ('Comida rápida, comida al paso (cocina)', '9.3'),
        ('Comida rápida, comida al paso (área de mesas, área de atención)', '1.5'),
        ('Locales de expendio de combustibles y/o de energía eléctrica', 'En función de los servicios complementarios que cuente'),
        ('Locales bancarios y de intermediación financiera', '5.0'), ('#Locales de entretenimiento y/o recreo', ''),
        ('Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)', '4.0'),
        ('#Locales de servicios personales', ''), ('Spa, baño turco, sauna, baño de vapor', '3.4'), ('Barbería, salón de belleza', '2.4'),
        ('Gimnasio, fisicoculturismo (área con máquinas)', '4.6'), ('Gimnasio, fisicoculturismo (área sin máquinas)', '1.4'),
        ('Tienda por departamentos', '3.0'), ('#Tienda de autoservicio', ''), ('Supermercado', '2.5'), ('Tienda de mejoramiento del hogar', '3.0'),
        ('Otras tiendas de autoservicio', '2.5'), ('#Locales de servicios para vehículos', ''), ('Local de estacionamiento de vehículos', '27.5'),
        ('Local de venta, mantenimiento y/o limpieza de vehículos', '37.7'), ('#Mercado de abastos', ''), ('Mercado de abastos mayorista', '5.0'),
        ('Mercado de abastos minorista', '2.0'), ('Galería comercial', '2.0'),
        ('Centro comercial', 'En función a la sumatoria total de las áreas de venta de los cálculos resultantes de ocupantes de los establecimientos que lo conforman'),
        ('Galería ferial', '2.0'), ('Depósitos y almacenes al interior de ocupaciones comerciales', '27.9')]
T[('A070', 'Cuadro N° 3')] = dict(
    h=['Clasificación|Coeficiente de ocupación'],
    r=[a if a.startswith('#') else f'{a}|{b + " m² por persona" if re.match(r"^[0-9.]+$", b) else b}' for a, b in _occ],
    end='8.2 Para los casos')
T[('A070', 'Cuadro N° 4')] = dict(
    h=['Tipo de vano|Ancho mínimo'],
    r=['Ingreso principal|1.00 m', 'Dependencias interiores|0.90 m', 'Servicios higiénicos|0.80 m', 'Servicios higiénicos para discapacitados|0.90 m'])
T[('A070', 'Cuadro N° 5')] = dict(
    h=['Tipo de pasajes de circulación|Ancho mínimo'],
    r=['Interior de locales comerciales individuales: ancho mínimo entre góndolas, anaqueles o exhibidores de 1.20 m de altura que contienen productos de consumo cotidiano|0.90 m',
       'Interior de locales comerciales, entre góndolas o anaqueles de consumo cotidiano, y para productos especializados cuando las dimensiones del producto lo permitan|1.20 m',
       'Pasajes secundarios por los que se accede a tiendas o locales dentro de un local comercial agrupado|2.40 m',
       'Pasajes principales por los que se accede a tiendas o locales dentro de un local comercial agrupado|3.00 m'])
T[('A070', 'Cuadro N° 6')] = dict(
    h=['Tipo de ambientes|Área mínima'],
    r=['Carnes, pescado y productos perecibles, abarrotes, mercería|4 m²', 'Cocina|6 m²', 'Otros productos|5 m²'])
T[('A070', 'Cuadro N° 21')] = dict(
    h=['Clasificación|Estacionamientos|<', '^|Para personal administrativo|Para público'],
    r=['Tienda independiente|1 est. cada 15 personas|1 est. cada 15 personas',
       '#Locales de expendio de comidas y bebidas',
       'Restaurante, cafetería (área de mesas); comida rápida o al paso (área de mesas, área de atención)|1 est. cada 20 pers.|1 est. cada 20 pers.',
       'Locales de expendio de combustibles y/o de energía eléctrica|En función de los servicios complementarios que contiene|<',
       'Locales bancarios y de intermediación financiera|1 est. cada 15 pers.|1 est. cada 10 pers.',
       '#Locales de entretenimiento y/o recreo',
       'Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)|1 est. cada 25 pers.|1 est. cada 25 pers.',
       '#Locales de servicios personales',
       'Spa, baños turcos, sauna, baños de vapor, barbería, salones de belleza; gimnasios, fisicoculturismo|1 est. cada 15 pers.|1 est. cada 10 pers.',
       'Tienda por departamentos|1 est. cada 25 pers.|1 est. cada 25 pers.',
       '#Tienda de autoservicio',
       'Supermercado, tienda de mejoramiento del hogar, otras tiendas de autoservicio|1 est. cada 20 pers.|1 est. cada 20 pers.',
       '#Mercado de abastos',
       'Mercado de abastos mayorista y minorista|1 est. cada 10 pers.|1 est. cada 10 pers.',
       'Galería comercial|1 est. cada 25 pers.|1 est. cada 20 pers.',
       'Centro comercial|En función a la sumatoria total de los cálculos resultantes de estacionamientos de los establecimientos que lo conforman|<',
       'Galería ferial|1 est. cada 25 pers.|1 est. cada 20 pers.'],
    n=['Donde el texto fuente pone un solo valor para varias filas de un grupo, aquí van juntas en una fila.'],
    end='b) Este a su vez')
T[('A070', 'Cuadro N° 22')] = dict(
    h=['Tipo de comercio|Población a servir|Costa|<|Sierra|Selva', '^|^|Lima|Otras ciudades|^|^'],
    r=['Comercio interdistrital y metropolitano (CM)|Más de 300,000 hab.|1.0|0.8|0.8|0.7',
       'Comercio distrital (CZ)|100,000 – 300,000 hab.|0.7|0.7|0.6|',
       'Comercio zonal o sectorial (CZ)|30,000 – 100,000 hab.|0.9|0.6|0.6|0.5',
       'Comercio local y vecinal (CV)|Hasta 30,000 hab.|0.6|0.4|0.4|0.3'],
    n=['En el texto fuente la fila «Comercio distrital» tiene solo tres valores: no se sabe a qué columna le falta uno.'])
T[('A070', 'Cuadro N° 23')] = dict(h=['Tipo de vehículo|Porcentaje requerido'], r=['Autos|60%', 'Motos|10%', 'Vehículos menores|30%'])
T[('A070', 'Cuadro N° 24')] = dict(
    h=['Índice|Estacionamientos de carga'],
    r=['De 1 a 500 m² de área techada|1', 'De 501 a 1,500 m² de área techada|2', 'De 1,501 a 3,000 m² de área techada|3', 'Más de 3,000 m² de área techada|4'])
T[('A070', 'Cuadro N° 25')] = dict(
    h=['Índice|Estacionamientos de carga'],
    r=['Hasta 1,500 m² de área techada|1', 'De 1,501 a 3,000 m² de área techada|2', 'Cada 3,000 m² adicionales|1'])
_res = [('Tienda independiente', '0.003'), ('#Locales de expendio de comidas y bebidas', ''), ('Restaurante, cafetería', '0.015'),
        ('Comida rápida, o al paso', '0.030'), ('Locales de expendio de combustibles y/o de energía eléctrica', '0.0001'),
        ('Locales bancarios y de intermediación financiera', '0.003'), ('#Locales de entretenimiento y/o recreo', ''),
        ('Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)', '0.003'),
        ('#Locales de servicios personales', ''), ('Spa, baños turcos, sauna, baños de vapor, barbería, salones de belleza; gimnasios, fisicoculturismo', '0.003'),
        ('Tienda por departamentos', '0.003'), ('Tienda de autoservicio: supermercado, tienda de mejoramiento del hogar, otras', '0.003'),
        ('Locales de servicios para vehículos: estacionamiento; venta, mantenimiento y/o limpieza', '0.003'),
        ('#Mercado de abastos', ''), ('Mercado de abastos mayorista', '0.015'), ('Mercado de abastos minorista', '0.020'),
        ('Galería comercial', '0.003'), ('Centros comerciales', 'En base al área de venta de los establecimientos que lo conforman'), ('Galería ferial', '0.003')]
T[('A070', 'Cuadro N° 26')] = dict(
    title='Cuadro N° 26. Factor para determinar el área mínima de ambientes de acopio y evacuación de residuos sólidos',
    h=['Clasificación|Acopio y evacuación de residuos'],
    r=[a if a.startswith('#') else f'{a}|{b + " m³ por m² de área de venta" if re.match(r"^[0-9.]+$", b) else b}' for a, b in _res],
    end='18.5')


def fold(t):
    import unicodedata
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[°º]', 'o', re.sub(r'\s+', ' ', t)).lower().strip()


def find(norm, title):
    f = fold(title)
    best = None
    for (n, k), v in T.items():
        fk = fold(k)
        if n == norm and f.startswith(fk) and (len(f) == len(fk) or not f[len(fk)].isdigit()):
            if best is None or len(fk) > len(fold(best[0])):
                best = (k, v)
    return best[1] if best else None


def sanitarios(rows):
    """Cuadros 7 a 20 de la A.070: «De 1 hasta 6 empleados 1L, 1U, 1I 1L, 1I»."""
    h, r, n = [], [], []
    MEN = re.compile(r'(\d+L, ?\d+[Uu], ?\d+I)')
    WOM = re.compile(r'(\d+L, ?\d+I)')
    for line in rows:
        if line.startswith('Número de'):
            parts = line.split()
            hdr = ' '.join(parts[:-2]) + '|Hombres|Mujeres'
            (h if not h else r).append(hdr if not h else '#' + ' '.join(parts[:-2]))
            continue
        if line.startswith('L ='):
            n.append(line); continue
        m = MEN.search(line)
        if 'No requiere' in line:
            r.append(line.replace('No requiere', '').strip() + '|No requiere|<'); continue
        if not m:
            r.append(line + '||'); continue
        label = line[:m.start()].strip(); rest = line[m.end():].strip()
        w = WOM.search(rest)
        r.append(f'{label}|{m.group(1)}|{w.group(1)}' if w else f'{label}|{m.group(1)}|<')
    return dict(h=h, r=r, n=n)


def pozos(rows):
    """Cuadro 10 de la A.020: distancias por altura y tramo."""
    r = []
    tramo = None
    last = None
    pend_pct = False
    for line in rows:
        m = re.match(r'^TRAMO (\d+)', line)
        if m:
            tramo = m.group(1); pend_pct = True; continue
        if pend_pct and re.match(r'^(\d+% ?){4}$', line):
            p = line.split()
            if tramo != last:
                r.append(f'#Tramo {tramo}: pozo de 1 a 2 lados A {p[0]}, B {p[1]} · pozo de 3 a 4 lados A {p[2]}, B {p[3]}')
                last = tramo
            pend_pct = False; continue
        if re.match(r'^\d+ [\d.]+ [\d.]+ [\d.]+ [\d.]+$', line):
            r.append('|'.join(line.split()))
    return dict(h=['Altura (m)|Pozo de 1 a 2 lados|<|Pozo de 3 a 4 lados|<', '^|A|B|A|B'], r=r,
                n=['Distancias perpendiculares al vano, en metros. A = dormitorios, salas y comedores; B = cocinas y patios techados.'])

# A.130 (texto de 2006): tablas 1 a 3, transcritas de la separata impresa (págs. 140-142)
_cat = 'Resistencia al fuego ({a} Hrs)|Semi resist. al fuego ({b} Hrs)|Incombust. con protección (1 Hrs)'
T[('A130', 'TABLA Nº 1')] = dict(
    title='Tabla Nº 1. Recubrimientos mínimos de protección al fuego en elementos estructurales',
    h=['Elementos estructurales protegidos|Material aislante|Recubrimiento mínimo por material aislante (en pulgadas), categorías|<|<',
       '^|^|' + _cat.format(a=6, b=6)],
    r=['Armaduras en vigas y columnas de concreto armado|Concreto estructural|1 1/2|1 1/2|1 1/2',
       'Armadura en viguetas de concreto|Concreto estructural|1 1/4|1|3/4',
       'Armaduras y amarres en losas de pisos y techos|Concreto estructural|1|3/4|3/4',
       'Columnas de acero y todos los elementos de tijerales principales|Concreto estructural|2 1/2|1 1/2|1',
       'Elementos de 6 x 6|Concreto estructural|2|1|1',
       'Elementos de 6 x 8|Concreto estructural|1 1/2|1|1',
       'Elementos de 12 x 12|Concreto estructural|2|1|1',
       'Vigas de acero; tendones en vigas pre o post esforzadas|Concreto estructural|4|2 1/2|1 1/2',
       'Tendones en placas pre o post esforzadas|Concreto estructural||1 1/2|1'],
    n=['Transcrita de la separata impresa (pág. 140). La segunda categoría dice «(6 Hrs)» en el original.'],
    end='Este espesor se protegerá')
T[('A130', 'TABLA Nº 2')] = dict(
    title='Tabla Nº 2. Espesores mínimos para protección al fuego en pisos, techos y cielo raso',
    h=['Construcción de pisos o techos|Construcción de cielo raso|Espesor mínimo total en pulgadas, categorías|<|<',
       '^|^|' + _cat.format(a=4, b=2)],
    r=['Losa de concreto|Ninguno|6 1/2|4 1/2|3 1/2',
       'Losa de concreto|Enlucido de yeso o mortero contra el fondo del techo|6|4|3',
       'Aligerado de viguetas de concreto estructural y ladrillo hueco de techos|Enlucido de yeso o mortero contra el fondo del techo||6” de ladrillo y 2” de losa|',
       'Aligerado de viguetas de concreto estructural y ladrillo hueco de techos|Ninguno|||5 ½ (4” de ladrillo y 1 ½” de losa)',
       'Viguetas de concreto|Cielo raso suspendido de vermiculita de 1” de espesor mínimo colgado 6” debajo de las viguetas|3 (sólo losa)|2 (sólo losa)|',
       'Viguetas de acero con losa de concreto|Cielo raso enlucido en malla incombustible asegurada contra el fondo de las viguetas, de espesor mínimo 5/8” y mortero 1:3||2 ¼” (sólo losa)|2” (sólo losa) Combustible e Construcción pesada'],
    n=['Transcrita de la separata impresa (pág. 141). La última celda está tal como se imprimió.'],
    end='Artículo')
T[('A130', 'TABLA Nº 3')] = dict(
    title='Tabla Nº 3. Espesores mínimos para protección al fuego en paredes y tabiques',
    h=['Materiales de paredes o tabiques|Construcción|Espesor mínimo total en pulgadas, categorías|<|<',
       '^|^|' + _cat.format(a=4, b=2)],
    r=['Concreto armado|Sólido sin enlucir|6 1/2|4 1/2|3 1/2',
       'Ladrillos de arcilla cocida, calcáreos o de:|Ladrillos sólidos sin enlucir|8|6|4',
       'Bloques huecos de concreto|Espesor mínimo de cascarón 2 ¼” sin enlucir|8||',
       '^|Espesor mínimo de cascarón 1 3/4” sin enlucir|12||',
       '^|Espesor mínimo de cascarón 1 3/8” sin enlucir||8|6',
       'Ladrillos huecos de arcilla cocida, no portantes|Dos celdas mínimo dentro del espesor de la pared, enlucido en ambas caras||7|5',
       '^|Tres celdas mínimo dentro del espesor de la pared, enlucido en ambas caras|12||',
       'Bloqueo|Enlucido o sin enlucir|6|4|3',
       'Tabique sólido de mortero o yeso|Armazón interno incombustible|||2',
       'Paneles de yeso prensado||||2'],
    n=['Transcrita de la separata impresa (págs. 141-142).'],
    end='Artículo')
T[('A130', 'Tabla 02: Área de Almacenes')] = dict(
    title='Tabla 02: Área de almacenes no techados que requieren protección mediante una red de agua contra incendios',
    h=['Riesgo / tipo|Área mínima que requiere protección (m²)'],
    r=['Clase I|5 000', 'Clase II|4 000', 'Clase III|2 500', 'Clase IV|1 000', 'Fardos de algodón|2 500', 'Papel en rollos|2 000',
       'Papel de reciclaje|2 000', 'Plásticos|900', 'Cajas y paletas vacías (madera)|1 000', 'Llantas|1 000', 'Patio de contenedores|10 000'],
    n=['El área mínima que requiere protección incluye el área de almacenamiento y la circulación interior.'],
    end='Artículo')

# ---- revisadas contra los PDF oficiales (rne/oficial/) ----
T[('A070', 'Cuadro N° 21')] = dict(
    h=['Clasificación|Estacionamientos|<', '^|Para personal administrativo|Para público'],
    r=['Tienda independiente|1 est. cada 15 personas|1 est. cada 15 personas',
       '#Locales de expendio de comidas y bebidas',
       'Restaurante, cafetería (área de mesas)|1 est. cada 20 pers.|1 est. cada 20 pers.',
       'Comida rápida, o al paso (área de mesas, área de atención)|^|^',
       'Locales de expendio de combustibles y/o de energía eléctrica|En función de los servicios complementarios que contiene|<',
       'Locales bancarios y de intermediación financiera|1 est. cada 15 pers.|1 est. cada 10 pers.',
       '#Locales de entretenimiento y/o recreo',
       'Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)|1 est. cada 25 pers.|1 est. cada 25 pers.',
       '#Locales de servicios personales',
       'Spa, baños turcos, sauna, baños de vapor, barbería, salones de belleza|1 est. cada 15 pers.|1 est. cada 10 pers.',
       'Gimnasios, fisicoculturismo|^|^',
       'Tienda por departamentos|1 est. cada 25 pers.|1 est. cada 25 pers.',
       '#Tienda de autoservicio',
       'Supermercado|1 est. cada 20 pers.|1 est. cada 20 pers.', 'Tienda de mejoramiento del hogar|^|^', 'Otras tiendas de autoservicio|^|^',
       '#Mercado de abastos',
       'Mercado de abastos mayorista|1 est. cada 10 pers.|1 est. cada 10 pers.', 'Mercado de abastos minorista|^|^',
       'Galería comercial|1 est. cada 25 pers.|1 est. cada 20 pers.',
       'Centro comercial|En función a la sumatoria total de los cálculos resultantes de estacionamientos de los establecimientos que lo conforman|<',
       'Galería ferial|1 est. cada 25 pers.|1 est. cada 20 pers.'],
    end='b) Este a su vez')
T[('A070', 'Cuadro N° 22')] = dict(
    h=['Tipo de comercio|Población a servir|Costa|<|Sierra|Selva', '^|^|Lima|Otras ciudades|^|^'],
    r=['Comercio interdistrital y metropolitano (CM)|Más de 300,000 hab.|1.0|0.8|0.8|0.7',
       'Comercio distrital (CZ)|100,00 – 300,000 hab.|^|0.7|0.7|0.6',
       'Comercio zonal o sectorial (CZ)|30,00 – 100,000 hab.|0.9|0.6|0.6|0.5',
       'Comercio local y vecinal (CV)|Hasta 30,000 hab.|0.6|0.4|0.4|0.3'])
_res2 = ['Tienda independiente|0.003', '#Locales de expendio de comidas y bebidas', 'Restaurante, cafetería|0.015', 'Comida rápida, o al paso|0.030',
         'Locales de expendio de combustibles y/o de energía eléctrica|0.0001', 'Locales bancarios y de intermediación financiera|0.003',
         '#Locales de entretenimiento y/o recreo', 'Parques de diversión y/o recreo, salas de juegos (electrónicos, video, bowling, de mesa, entre otros)|0.003',
         '#Locales de servicios personales', 'Spa, baños turcos, sauna, baños de vapor, barbería, salones de belleza|0.003', 'Gimnasios, fisicoculturismo|^',
         'Tienda por departamentos|0.003', '#Tienda de autoservicio', 'Supermercado|0.003', 'Tienda de mejoramiento del hogar|^', 'Otras tiendas de autoservicio|^',
         '#Locales de servicios para vehículos', 'Local de estacionamiento de vehículos|0.003', 'Local de venta, mantenimiento y/o limpieza de vehículos|^',
         '#Mercado de abastos', 'Mercado de abastos mayorista|0.015', 'Mercado de abastos minorista|0.020', 'Galería comercial|0.003',
         'Centros comerciales|En base a la área de venta de los establecimientos que la conforman', 'Galería ferial|0.003']
T[('A070', 'Cuadro N° 26')] = dict(T[('A070', 'Cuadro N° 26')],
    r=[x if x.startswith('#') or not re.search(r'\|[0-9.]+$', x) else x + ' m³ por m² de área de venta' for x in _res2])

S, N = '✓', 'X'
def _r(*cells): return '|'.join(cells)
_c27 = [
 _r('Tienda independiente (14)', '<', 'Área techada hasta 100 m²', S, S, N, N, N),
 _r('^', '^', 'Área techada mayor a 100 m² hasta 750 m²', S, S, N, N, S + ' (1)'),
 _r('^', '^', 'Área techada mayor a 750 m² hasta 1500 m²', S, S, S + ' (2)', N, S),
 _r('^', '^', 'Planta techada de área mayor a 1500 m²', S, S, S, S, S),
 _r('Locales de expendio de comidas y bebidas', 'Restaurante, cafetería, local de comida rápida, local de venta de comidas al paso', 'Área total construida hasta 75 m²', S, S, N, N, N),
 _r('^', '^', 'Área total construida mayor a 75 m² hasta 300 m²', S + ' (6)', S, N, N, S + ' (5)'),
 _r('^', '^', 'Área total construida mayor a 300 m²', S, S, N, N, S),
 _r('Locales de expendio de combustibles y/o energía eléctrica', 'Establecimiento de venta de combustibles (estación de servicio, grifo, gasocentro) y/o de energía eléctrica para vehículos', '<',
    'Los requisitos de seguridad que se requieren son en función de los servicios complementarios que contiene.', '<', '<', '<', '<'),
 _r('Locales bancarios y de intermediación financiera', '<', 'Área techada hasta 100 m²', S, S, N, N, N),
 _r('^', '^', 'Área techada mayor a 100 m² hasta 750 m²', S, S, N, N, S + ' (1)'),
 _r('^', '^', 'Área techada mayor a 750 m² hasta 1,500 m²', S, S, S + ' (2)', N, S),
 _r('^', '^', 'Planta techada de área mayor a 1,500 m²', S, S, S, S, S),
 _r('Locales de recreación y entretenimiento', 'Locales de diversiones y/o recreo', 'Área techada hasta 100 m²', S, S, N, N, N),
 _r('^', '^', 'Área mayor a 100 m² hasta 750 m²', S, S, S + ' (2) (8)', N, S),
 _r('^', '^', 'Área mayor a 750 m²', S, S, S, S, S),
 _r('Locales de servicios personales', 'Spa, baños turcos, sauna, baños de vapor, barbería, salones de belleza', 'Área techada hasta 100 m²', S, S, N, N, N),
 _r('^', '^', 'Área mayor a 100 m² hasta 750 m²', S, S, S + ' (2)', N, S),
 _r('^', '^', 'Área mayor a 750 m²', S, S, S, S, S),
 _r('^', 'Gimnasios, fisicoculturismo', 'Área techada hasta 100 m²', S, S, N, N, N),
 _r('^', '^', 'Área mayor a 100 m² hasta 750 m²', S, S, S + ' (2)', N, S),
 _r('^', '^', 'Área mayor a 750 m²', S, S, S, S, S),
 _r('Tienda por departamentos', '<', '<', S, S, S, S, S),
 _r('Tienda de autoservicio', 'Supermercado', 'De un (1) solo nivel y hasta 1,000 m² de área de venta', S, S, N, N, S),
 _r('^', '^', 'De un (1) solo nivel y área de venta mayor a 1,000 m² hasta 2,000 m²', S, S, S + ' (2)', N, S),
 _r('^', '^', 'De un (1) solo nivel mayor a 2,000 m² de área de venta', S, S, S, S, S),
 _r('^', '^', 'Entre uno (1) y tres (3) niveles, con área de venta hasta 1,000 m² por piso', S, S, N, N, S),
 _r('^', '^', 'De más de tres (3) niveles y área de venta hasta 1000 m² por piso', S, S, N, S, S),
 _r('^', '^', 'De más de un (1) nivel y área de venta mayor a 1,000 m² por piso', S, S, S, S, S),
 _r('^', 'Tienda de mejoramiento del hogar', '<', S, S, S, S, S),
 _r('^', 'Otras tiendas de autoservicio', '<', '', '', '', '', ''),
 _r('Mercados de abasto', 'Mercado de abastos mayorista (3)', 'Con techo común', S, S, S, S, S),
 _r('^', '^', 'Sin techo común (puestos independientes)', S, S, N, S, S),
 _r('^', 'Mercado de abastos minorista', 'Con techo común', S, S, N, S, S),
 _r('^', '^', 'Sin techo común (puestos independientes)', S, S, N, N, S + ' (15)'),
 _r('Galería comercial (7) (12)', '<', 'De un (1) solo nivel hasta 500 m² de área techada', S, S, N, N, S),
 _r('^', '^', 'De un (1) solo nivel y área techada mayor a 500 m² y hasta 1000 m²', S, S, N, S, S),
 _r('^', '^', 'De un (1) solo nivel y área techada mayor a 1000 m²', S, S, S + ' (2)', S, S),
 _r('^', '^', 'De dos (2) a tres (3) niveles, con área techada total hasta 1000 m²', S, S, N, N, S),
 _r('^', '^', 'De dos (2) a tres (3) niveles, con área techada total mayor a 1000 m²', S, S, N, S, S),
 _r('^', '^', 'De cuatro (4) a más niveles', S, S, S, S, S),
 _r('Centro comercial (13)', '<', 'De área hasta 500 m² por piso y hasta tres (3) niveles (3)', S, S, N, N, S),
 _r('^', '^', 'De área hasta 500 m² por piso y más de tres (3) niveles', S, S, N, S, S),
 _r('^', '^', 'De área mayor a 500 m² y hasta 1500 m² por piso y hasta tres (3) niveles (3)', S, S, N, S, S),
 _r('^', '^', 'De área mayor a 1500 m² por piso (4)', S, S, S, S, S),
 _r('Galería ferial', '<', '<', S + ' (9)', S, N, N, N),
]
T[('A070', 'Cuadro N° 27')] = dict(
    h=['Clasificación|Servicio|Características|Señalización e iluminación de emergencia|Extintores portátiles|Sistema de rociadores (10)|Sistema de gabinetes contra incendios|Detección y alarma de incendios centralizado (11)'],
    r=_c27,
    n=['✓ requiere · X no requiere. Los números entre paréntesis remiten a las notas:',
       '(1) A partir de 250 m² de área.',
       '(2) Cuando los requerimientos de agua (caudal y presión) del sistema de rociadores puedan ser abastecidos por el servicio de agua de la localidad, estos pueden conectarse directamente con la red pública, siempre y cuando exista una compañía de bomberos en la localidad.',
       '(3) Es requisito obligatorio contar con hidrantes que provean un caudal total mínimo de 750 gpm (caudales sumados).',
       '(4) Son requeridos hidrantes de la red pública con un caudal suficiente para el máximo riesgo, de acuerdo con la fórmula ISO.',
       '(5) Únicamente estaciones manuales y alarma de incendios.',
       '(6) Cuando las rutas de evacuación así lo exijan.',
       '(7) Para construcciones de conjunto de tiendas aplica los mismos requerimientos de protección contra incendio.',
       '(8) Únicamente aquellos ubicados bajo el nivel del piso.',
       '(9) Iluminación de emergencia solo requerido si hay atención al público sin iluminación natural.',
       '(10) Las áreas comerciales mayores a 250 m² ubicadas bajo el nivel del piso, deben contar con un sistema automático de rociadores. (2)',
       '(11) Los sistemas de detección y alarma deben reportar a un lugar con personal entrenado las 24 horas, o reportar vía telefónica a un punto que cumpla con estos requisitos.',
       '(12) Las tiendas de hasta tres (3) niveles colindantes con otras tiendas y/u otros predios, agrupadas formando 24.00 m lineales de frente, deben contar con muros laterales y posteriores resistentes al fuego no menor a una (1) hora y dos (2) horas para tiendas de cuatro (4) a más niveles. No se requiere compartimentación resistente al fuego en el frente de las tiendas.',
       '(13) En centros comerciales bajo un mismo techo estructural, la distancia máxima de recorrido es de 45.00 m a una salida de evacuación o de la edificación cuando no se cuenta con un sistema de rociadores, y de 60.00 m cuando la edificación cuenta con rociadores. Puede tener una distancia máxima de recorrido de 60.00 m adicionales, tomados desde la puerta de salida de la tienda hasta la salida más cercana de la edificación siempre que cuente con todos los siguientes componentes: a) rociadores instalados en el 100% del centro comercial, incluyendo áreas comunes de circulación techadas; b) sistema de administración de humos; c) compartimentación resistente al fuego no menor de 1 hora entre locales, para centros comerciales de hasta tres (3) pisos y de dos (2) horas de cuatro (4) pisos a más.',
       '(14) Las tiendas ubicadas al interior de centros comerciales y galerías comerciales deben cumplir los requisitos de resistencia al fuego en relación al local donde se ubican.',
       'La nota (15) aparece en el cuadro pero no figura en la lista de notas de la separata.'],
    end='Artículo')

_rf_h = ['Uso de la edificación|Sistema de rociadores|Tiempo de resistencia al fuego mínimo en minutos para:|<|<|<|<|<',
         '^|^|Sótanos: profundidad del sótano más bajo (NPT)|<|Pisos superiores: altura del piso superior sobre el nivel de descarga de los ocupantes|<|<|<',
         '^|^|> 10 m|≤ 10 m|≤ 5 m|≤ 21 m|≤ 60 m|> 60 m']
_rf_n = ['NP: no permitido.', '(2) Mayores a 3,7 metros de altura de carga de combustible.']
T[('A130', 'Tabla 01: Tiempo mínimo')] = dict(
    title='Tabla 01: Tiempo mínimo permitido de resistencia al fuego para los elementos estructurales: pórticos, muros, arcos, losas',
    h=_rf_h,
    r=['#Almacenes (2)', 'Bajo riesgo (3)|NO|120|90|60|90|120|NP', '^|SI|120|90|60|90|90|120',
       'Moderado riesgo (3)|NO|180|120|90|120|180|NP', '^|SI|120|90|60|90|120|180', 'Alto riesgo (3)|NO|NP|NP|120|180|NP|NP',
       'Líquidos inflamables y combustibles (3)|NO|NP|NP|120|180|NP|NP', '^|SI|NP|NP|90|120|180|NP'],
    n=_rf_n + ['(3) Clasificación de riesgos establecidos en norma A-010 edición 2009, Artículo 25.'],
    end='El proceso de ensayo')
T[('A130', 'Tabla 06')] = dict(
    title='Tabla 06: Tiempo mínimo permitido de resistencia al fuego para los elementos estructurales: pórticos, muros, arcos, losas',
    h=_rf_h,
    r=['#Almacenes (2)', 'Bajo riesgo (3)|NO|120|90|60|90|120|NP', '^|SI|120|90|60|90|90|120',
       'Moderado riesgo (3)|NO|180|120|90|120|180|NP', '^|SI|120|90|60|90|120|180', 'Alto riesgo (3)|NO|NP|NP|120|180|NP|NP',
       'Líquidos inflamables y combustibles (3)|NO|NP|NP|180|180|NP|NP', '^|SI|NP|NP|120|120|180|NP'],
    n=_rf_n + ['(3) Clasificación de riesgos establecidos en norma A-130 edición 2009, Artículo 25.'],
    end='El proceso de ensayo')
_alm_h = ['Tipo de mercancía|Área de almacenamiento (m²)|Sistema de rociadores|Sistema de agua (gabinetes)|Sistema de detección de incendios / alarma|Extintores portátiles|Señalización']
def _alm(rows):
    out = []
    for clase, a1, r1, a2, r2 in rows:
        out += [f'{clase}|{a1}|{r1}', f'^|{a2}|{r2}']
    return out
T[('A130', 'Tabla 03')] = dict(
    title='Tabla 03: Requerimiento mínimo de protección contra incendios para almacenes techados, de altura menor a 3,70 m y que constituye el principal o único uso de ocupación',
    h=_alm_h,
    r=_alm([('Clase I', '0-2500', 'NO|NO|SI|SI|SI', '> 2501', 'NO|SI|SI|SI|SI'), ('Clase II', '0-2500', 'NO|NO|SI|SI|SI', '> 2501', 'NO|SI|SI|SI|SI'),
            ('Clase III', '0-1500', 'NO|SI|SI|SI|SI', '> 1501', 'SI|SI|SI|SI|SI'), ('Clase IV', '0-1000', 'NO|SI|SI|SI|SI', '> 1001', 'SI|SI|SI|SI|SI')]),
    end='Nota: Para almacenamientos')
T[('A130', 'Tabla 04:')] = dict(
    title='Tabla 04: Requerimiento mínimo de protección contra incendios para almacenes techados, de altura mayor a 3,70 m y menor a 7,60 m',
    h=_alm_h,
    r=_alm([('Clase I', '0-2500', 'NO|NO|SI|SI|SI', '> 2501', 'NO|SI|SI|SI|SI'), ('Clase II', '0-2500', 'NO|NO|SI|SI|SI', '> 2501', 'SI|SI|SI|SI|SI'),
            ('Clase III', '0-1500', 'NO|SI|SI|SI|SI', '> 1501', 'SI|SI|SI|SI|SI'), ('Clase IV', '0-1000', 'NO|SI|SI|SI|SI', '> 1001', 'SI|SI|SI|SI|SI')]),
    end='1.5')
T[('A130', 'Tabla 05')] = dict(
    title='Tabla 05: Requerimiento mínimo de protección contra incendios para almacenes techados de altura mayor a 7,60 m',
    h=_alm_h,
    r=['Clase I|1500|SI|SI|SI|SI|SI', 'Clase II|1000|SI|SI|SI|SI|SI', 'Clase III|1000|SI|SI|SI|SI|SI', 'Clase IV|500|SI|SI|SI|SI|SI'],
    end='Artículo')
