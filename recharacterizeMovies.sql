UPDATE recorded
SET recgroup = 'movies'
WHERE category = 'Movie';


UPDATE recorded       
SET recgroupid = 4
WHERE category = 'Movie';

UPDATE record
SET recgroup = 'movies'
WHERE category = 'Movie';


UPDATE record       
SET recgroupid = 4
WHERE category = 'Movie';



(select * from recordedprogram where category = 'Movie');
