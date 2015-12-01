import sys
sys.path.append('/opt/OpenvStorage')

from ovs.dal.helpers import Migration
Migration.migrate()
