"""empty message

Revision ID: 223568d6d7d6
Revises: 
Create Date: 2019-04-09 09:42:30.662133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '223568d6d7d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_genres',
    sa.Column('book_genre_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('book_genre_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('book_genre_id')
    )
    op.create_table('fav_cuisines',
    sa.Column('fav_cuisine_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fav_cuisine_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('fav_cuisine_id')
    )
    op.create_table('hobbies',
    sa.Column('hobby_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('hobby_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('hobby_id')
    )
    op.create_table('movie_genres',
    sa.Column('movie_genre_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('movie_genre_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('movie_genre_id')
    )
    op.create_table('music_genres',
    sa.Column('music_genre_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('music_genre_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('music_genre_id')
    )
    op.create_table('outdoors',
    sa.Column('outdoor_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('outdoor_activity', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('outdoor_id')
    )
    op.create_table('religions',
    sa.Column('religion_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('religion_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('religion_id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('firstname', sa.String(length=100), nullable=False),
    sa.Column('lastname', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('date_of_birth', sa.String(length=100), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=100), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('interests',
    sa.Column('interest_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('book_genre_id', sa.Integer(), nullable=False),
    sa.Column('movie_genre_id', sa.Integer(), nullable=False),
    sa.Column('music_genre_id', sa.Integer(), nullable=False),
    sa.Column('fav_cuisine_id', sa.Integer(), nullable=False),
    sa.Column('hobby_id', sa.Integer(), nullable=False),
    sa.Column('religion_id', sa.Integer(), nullable=False),
    sa.Column('outdoor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_genre_id'], ['book_genres.book_genre_id'], ),
    sa.ForeignKeyConstraint(['fav_cuisine_id'], ['fav_cuisines.fav_cuisine_id'], ),
    sa.ForeignKeyConstraint(['hobby_id'], ['hobbies.hobby_id'], ),
    sa.ForeignKeyConstraint(['movie_genre_id'], ['movie_genres.movie_genre_id'], ),
    sa.ForeignKeyConstraint(['music_genre_id'], ['music_genres.music_genre_id'], ),
    sa.ForeignKeyConstraint(['outdoor_id'], ['outdoors.outdoor_id'], ),
    sa.ForeignKeyConstraint(['religion_id'], ['religions.religion_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('interest_id')
    )
    op.create_table('pending_matches',
    sa.Column('user_query_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('query_pin_code', sa.Integer(), nullable=False),
    sa.Column('query_time', sa.DateTime(), nullable=False),
    sa.Column('pending', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_query_id')
    )
    op.create_table('user_matches',
    sa.Column('match_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id_1', sa.Integer(), nullable=False),
    sa.Column('user_id_2', sa.Integer(), nullable=False),
    sa.Column('match_date', sa.DateTime(), nullable=False),
    sa.Column('user_2_status', sa.Boolean(), nullable=False),
    sa.Column('query_pincode', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['user_id_1'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id_2'], ['users.id'], ),
    sa.PrimaryKeyConstraint('match_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_matches')
    op.drop_table('pending_matches')
    op.drop_table('interests')
    op.drop_table('users')
    op.drop_table('religions')
    op.drop_table('outdoors')
    op.drop_table('music_genres')
    op.drop_table('movie_genres')
    op.drop_table('hobbies')
    op.drop_table('fav_cuisines')
    op.drop_table('book_genres')
    # ### end Alembic commands ###
