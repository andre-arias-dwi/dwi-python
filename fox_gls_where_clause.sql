AND STRUCT(traffic_source.source, traffic_source.medium) IN (
  STRUCT('facebook', 'organic_social'),
  STRUCT('fox', 'email'),
  STRUCT('fox', 'organic_social'),
  STRUCT('fox', 'radio'),
  STRUCT('fox', 'tv'),
  STRUCT('fox', 'web_others'),
  STRUCT('fox', 'website'),
  STRUCT('instagram', 'organic_social'),
  STRUCT('threads', 'organic_social'),
  STRUCT('x', 'organic_social'),
  STRUCT('youtube', 'organic_social')
)