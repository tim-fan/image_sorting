from image_sorting.competition_management import CompetitionManager
import tempfile

def test_simple_competition():

    with tempfile.TemporaryDirectory() as tempdir:

        manager = CompetitionManager(dbfile='{}/test_db.sqlite'.format(tempdir))

        # run simple competition.
        # competitors = ['a','b','c','d']
        # a beats b, d beats c, d beats a
        # final ranking: d wins, a runner up, b,d losers

        assert not manager.competition_in_progress()

        manager.start_competition(
            competitor_names=['a', 'b', 'c', 'd'],
            randomise=False
        )

        assert manager.get_n_remaining_matches() == 3

        assert set(manager.get_next_match()) == {'a', 'b'}
        manager.process_result(winner='a', loser='b')
        assert manager.get_n_remaining_matches() == 2

        assert set(manager.get_next_match()) == {'c', 'd'}
        manager.process_result(winner='d', loser='c')
        assert manager.get_n_remaining_matches() == 1

        assert set(manager.get_next_match()) == {'a', 'd'}
        manager.process_result(winner='d', loser='a')
        assert manager.get_n_remaining_matches() == 0

        rankings = manager.get_top_n(4)
        assert 'd' == rankings[0]
        assert 'a' == rankings[1]
        assert 'b' in rankings[2:4]
        assert 'c' in rankings[2:4]

        assert manager.get_next_match() is None

        del(manager) #required for tempdir to delete cleanly

def test_multi_user_comp():
    """
    Test multi-user use-case
    """
    with tempfile.TemporaryDirectory() as tempdir:

        manager = CompetitionManager(dbfile='{}/test_db.sqlite'.format(tempdir))
        manager.start_competition(
            competitor_names=['a', 'b', 'c', 'd'],
            randomise=False
        )
        #repeated call to 'get_next_match' should 
        #return different matches, 
        assert set(manager.get_next_match()) == {'a', 'b'}
        assert set(manager.get_next_match()) == {'c', 'd'}
        
        # once all competitors are in active matches,
        # manager can start returning active competitors
        assert set(manager.get_next_match()) == {'a', 'b'}

        
        del(manager) #required for tempdir to delete cleanly

