from yaml_parser import parse_all_yaml
from simple_html_parser import get_all_player_stats
from fix_deliveries_file import fix_deliveries_data, make_clusters
from clustering import create_clusters


parse_all_yaml()
get_all_player_stats()
create_clusters()
fix_deliveries_data()
make_clusters()