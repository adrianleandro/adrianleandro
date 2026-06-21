-- Insert default preference categories
INSERT INTO preference_categories (name, description) VALUES
('wine_types', '¿Qué tipo de vino te llama más la atención?'),
('bodies', '¿Cómo te gustaría que se sintiera el vino en tu boca?'),
('intensity', '¿Qué intensidad de sabor prefieres en tu vino?'),
('dryness', '¿Prefieres que se sienta suave o que deje una ligera sensación de sequedad?'),
('abv', '¿Qué tanto alcohol te gustaría que tenga el vino?');

-- Insert wine_types options
INSERT INTO preference_options (category_id, option, description, value)
SELECT pc.id, t.option, t.description, t.value 
FROM preference_categories pc, (VALUES
    ('Tinto', 'Rico y profundo en sabor', 1.0),
    ('Blanco', 'Ligero y refrescante', 2.0),
    ('Rosado', 'Una combinación de características de vinos tintos y blancos', 3.0),
    ('Espumoso', 'Burbujeante y festivo', 4.0)
) AS t(option, description, value)
WHERE pc.name = 'wine_types';

-- Insert bodies options
INSERT INTO preference_options (category_id, option, description, value)
SELECT pc.id, t.option, t.description, t.value 
FROM preference_categories pc, (VALUES
    ('Muy ligero', 'Como un sorbo delicado sin mucha presencia', 1.0),
    ('Ligero', 'Con algo más de presencia que el agua', 2.0),
    ('Medio', 'Equilibrado y fácil de beber', 3.0),
    ('Robusto', 'Un vino con sustancia notable', 4.0),
    ('De cuerpo completo', 'Intenso, robusto y con mucha presencia en el paladar', 5.0)
) AS t(option, description, value)
WHERE pc.name = 'bodies';

-- Insert intensity options
INSERT INTO preference_options (category_id, option, description, value)
SELECT pc.id, t.option, t.description, t.value 
FROM preference_categories pc, (VALUES
    ('Muy sutil', 'Una insinuación apenas perceptible del sabor', 1.0),
    ('Suave', 'Presente sin llegar a ser abrumador', 2.0),
    ('Equilibrada', 'Una buena mezcla de sabores que se hacen notar de manera constante', 3.0),
    ('Intensa', 'Los sabores se destacan con claridad', 4.0),
    ('Muy intensa', 'Una explosión de sabor en cada sorbo', 5.0)
) AS t(option, description, value)
WHERE pc.name = 'intensity';

-- Insert dryness options
INSERT INTO preference_options (category_id, option, description, value)
SELECT pc.id, t.option, t.description, t.value 
FROM preference_categories pc, (VALUES
    ('Muy suave', 'Sin sensación alguna de sequedad', 1.0),
    ('Mayormente suave', 'Con un leve toque de sequedad', 2.0),
    ('Textura moderada', 'Equilibrado, entre suavidad y un toque de sequedad', 3.0),
    ('Textura marcada', 'Se nota algo de sequedad en la lengua', 4.0),
    ('Fuerte textura', 'Una sensación de sequedad pronunciada que le da estructura al vino', 5.0)
) AS t(option, description, value)
WHERE pc.name = 'dryness';

-- Insert abv options
INSERT INTO preference_options (category_id, option, description, value)
SELECT pc.id, t.option, t.description, t.value 
FROM preference_categories pc, (VALUES
    ('Suave', 'Bajo contenido alcohólico (8-11%)', 9.5),
    ('Moderado', 'Contenido alcohólico medio (11-13.5%)', 12.25),
    ('Alto contenido alcohólico', 'Alto contenido alcohólico (13.5-16%+)', 14.75)
) AS t(option, description, value)
WHERE pc.name = 'abv';