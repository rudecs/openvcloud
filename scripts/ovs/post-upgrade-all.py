import sys
sys.path.append('/opt/OpenvStorage')

from ovs.extensions.migration.migrator import Migrator
Migrator.migrate()
