from sqlalchemy import (
    Column, String, Integer, ForeignKey, SmallInteger, Text
)
from sqlalchemy.orm import relationship

from dns_system.apps.db.abstract import IDBase, TimestampBase


class Domains(IDBase, TimestampBase):
    __tablename__ = "domains"

    cloudflare_domain_id = Column(String(64), index=True)
    domain_name = Column(String(128), unique=True)
    has_zone = Column(SmallInteger)
    checked_at = Column(Integer)


class DomainRecords(IDBase):
    __tablename__ = "domain_records"

    cloudflare_dns_record_id = Column(String(64), index=True)
    domain_id = Column(ForeignKey("domains.id", ondelete="CASCADE"))
    status = Column(SmallInteger)
    record_type = Column(String(300))
    record_content = Column(String(1000))
    record_proxied = Column(SmallInteger)
    record_ttl = Column(Integer)

    domain = relationship("Domains", lazy="joined")


class DomainDNSQueue(IDBase, TimestampBase):
    __tablename__ = "domain_dns_queue"

    domain_id = Column(ForeignKey("domains.id", ondelete="CASCADE"))
    status = Column(Integer)
    task = Column(Integer)

    domain = relationship("Domains", lazy="joined")


class DomainDNSLog(IDBase):
    __tablename__ = "domain_dns_log"

    queue_id = Column(ForeignKey("domain_dns_queue.id", ondelete="CASCADE"))
    task = Column(Integer)
    response = Column(Text)
    response_http_code = Column(Integer)
