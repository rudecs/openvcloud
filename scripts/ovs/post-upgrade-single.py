import sys
sys.path.append('/opt/OpenvStorage')

# model migration
from ovs.dal.helpers import Migration
Migration.migrate()
