import logging

from aleph.core import db, url_for
from aleph.model.common import TimeStampedModel, make_token
from aleph.model.user import User
from aleph.model.forms import SourceEditForm, SourceCreateForm

log = logging.getLogger(__name__)


source_user_table = db.Table('source_user', db.metadata,
    db.Column('source_id', db.Integer, db.ForeignKey('source.id')), # noqa
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')) # noqa
)


class Source(db.Model, TimeStampedModel):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Unicode, nullable=True)
    foreign_id = db.Column(db.Unicode, unique=True, nullable=False)
    public = db.Column(db.Boolean, default=True)

    users = db.relationship(User, secondary=source_user_table, backref='sources')  # noqa

    @classmethod
    def create(cls, data):
        foreign_id = data.get('foreign_id')
        src = Source.by_foreign_id(foreign_id)
        if src is not None:
            return src
        src = cls()
        data = SourceCreateForm().deserialize(data)
        src.foreign_id = foreign_id or make_token()
        src.update_data(data)
        db.session.add(src)
        db.session.flush()
        return src

    def update(self, data):
        data = SourceEditForm().deserialize(data)
        self.update_data(data)

    def update_data(self, data):
        self.label = data.get('label')
        self.public = data.get('public')
        self.users = list(set(data.get('users', [])))

    def delete(self):
        from aleph.model import Document, Page, Reference
        sq = db.session.query(Document.id)
        sq = sq.filter(Document.source_id == self.id)
        sq = sq.subquery()

        q = db.session.query(Page)
        q = q.filter(Page.document_id.in_(sq))
        q.delete(synchronize_session='fetch')

        q = db.session.query(Reference)
        q = q.filter(Reference.document_id.in_(sq))
        q.delete(synchronize_session='fetch')

        q = db.session.query(Document)
        q = q.filter(Document.source_id == self.id)
        q.delete(synchronize_session='fetch')

        db.session.delete(self)

    def to_dict(self):
        return {
            'api_url': url_for('sources.view', id=self.id),
            'id': self.id,
            'foreign_id': self.foreign_id,
            'label': self.label,
            'public': self.public,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()

    @classmethod
    def by_foreign_id(cls, foreign_id):
        if foreign_id is None:
            return
        return db.session.query(cls).filter_by(foreign_id=foreign_id).first()

    @classmethod
    def all(cls, ids=None):
        q = db.session.query(cls)
        if ids is not None:
            q = q.filter(cls.id.in_(ids))
        return q

    @classmethod
    def all_labels(cls, ids=None):
        q = db.session.query(cls.id, cls.label)
        if ids is not None:
            q = q.filter(cls.id.in_(ids))
        data = {}
        for (id, label) in q:
            data[id] = label
        return data

    def __repr__(self):
        return '<Source(%r)>' % self.id

    def __unicode__(self):
        return self.label
