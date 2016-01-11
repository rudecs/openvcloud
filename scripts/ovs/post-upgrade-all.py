import sys
sys.path.append('/opt/OpenvStorage')

# code migration
from ovs.extensions.migration.migrator import Migrator
Migrator.migrate()
