import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from m05_rag_evaluation_lab import retrieval_metrics as retrieval, answer_metrics as answer, abstention_metrics, mrr_at_k, GRADES, CLAIMS, REQUIRED

class RagEvaluationTests(unittest.TestCase):
    def test_mrr_includes_misses_and_reports_exclusions(self):
        queries=[{'id':'q1','ranked':['C','A'],'grades':GRADES},
                 {'id':'q2','ranked':['D'],'grades':{'D':3}},
                 {'id':'q3','ranked':['D'],'grades':{'C':3,'D':0}},
                 {'id':'q4','ranked':['D'],'grades':{'D':0}}]
        self.assertEqual(mrr_at_k(queries,2),{'mrr':.5,'eligible':3,'excluded':1})
    def test_mrr_no_eligible_queries_or_duplicate_ids(self):
        self.assertIsNone(mrr_at_k([],2)['mrr'])
        q={'id':'same','ranked':['A'],'grades':GRADES}
        with self.assertRaises(ValueError):mrr_at_k([q,q],2)
    def test_baseline_recall_and_rr(self):
        m=retrieval(['C','A','B','D'],GRADES,2)
        self.assertEqual(m['recall'],.5)
        self.assertEqual(m['rr'],.5)
        self.assertAlmostEqual(m['ndcg'],(7/1.584962500721156)/(7+3/1.584962500721156))
    def test_ideal_ranking(self):
        m=retrieval(['A','B','C','D'],GRADES,2)
        self.assertEqual((m['recall'],m['rr'],m['ndcg']),(1,1,1))
    def test_rank_order_matters_at_full_recall(self):
        self.assertLess(retrieval(['B','A'],GRADES,2)['ndcg'],1)
    def test_short_results_keep_denominators(self):
        m=retrieval(['A'],GRADES,4)
        self.assertEqual(m['recall'],.5)
        self.assertEqual(m['context_relevance'],1)
        self.assertLess(m['ndcg'],1)
    def test_no_relevant_is_undefined(self):
        m=retrieval(['C'],{'C':0},2)
        self.assertIsNone(m['recall']); self.assertIsNone(m['rr']); self.assertIsNone(m['ndcg'])
        self.assertEqual(m['context_relevance'],0)
    def test_empty_ranked_is_miss(self):
        self.assertEqual(retrieval([],GRADES,2)['recall'],0)
        self.assertIsNone(retrieval([],GRADES,2)['context_relevance'])
    def test_reject_unjudged_and_duplicates(self):
        for ranking in (['Z'],['A','A']):
            with self.assertRaises(ValueError):retrieval(ranking,GRADES,2)
    def test_invalid_inputs(self):
        for k in (0,-1,True,1.5):
            with self.assertRaises(ValueError):retrieval([],GRADES,k)
        for grade in (-1,4,True,1.5):
            with self.assertRaises(ValueError):retrieval([],{'A':grade},2)
    def test_full_answer(self):
        self.assertTrue(all(v==1 for v in answer(CLAIMS,['A','B'],REQUIRED).values()))
    def test_context_miss_can_still_be_factually_complete(self):
        m=answer(CLAIMS,['A'],REQUIRED)
        self.assertEqual(m['faithfulness'],.5); self.assertEqual(m['completeness'],1)
        self.assertEqual(m['citation_precision'],.5)
    def test_faithful_but_incomplete(self):
        m=answer(CLAIMS[:1],['A','B'],REQUIRED)
        self.assertEqual(m['faithfulness'],1); self.assertEqual(m['completeness'],.5)
    def test_wrong_citation_distinct_from_support(self):
        claims=[dict(CLAIMS[0],cites=['B'])]
        m=answer(claims,['A','B'],REQUIRED)
        self.assertEqual(m['faithfulness'],1); self.assertEqual(m['citation_precision'],0)
    def test_no_citations_cannot_hide_coverage(self):
        m=answer([dict(CLAIMS[0],cites=[])],['A'],REQUIRED)
        self.assertIsNone(m['citation_precision']); self.assertEqual(m['citation_coverage'],0)
    def test_abstain_no_perfect_faithfulness(self):
        m=answer([],['A'],REQUIRED)
        self.assertIsNone(m['faithfulness']); self.assertIsNone(m['citation_precision']); self.assertEqual(m['completeness'],0)
    def test_extra_unsupported_claim(self):
        claims=CLAIMS+[{'fact':'retry','correct':False,'supports':[],'cites':['C']}]
        m=answer(claims,['A','B','C'],REQUIRED)
        self.assertAlmostEqual(m['faithfulness'],2/3); self.assertEqual(m['completeness'],1)
    def test_required_facts_deduplicated_in_numerator(self):
        self.assertEqual(answer(CLAIMS+CLAIMS,['A','B'],REQUIRED)['completeness'],1)
    def test_empty_required_is_undefined(self):
        self.assertIsNone(answer([],[],[])['completeness'])
    def test_correct_and_false_abstentions(self):
        m=abstention_metrics([(True,True),(True,False),(False,True),(False,False)])
        self.assertEqual(m,{'correct_abstention':.5,'false_abstention':.5})
    def test_no_abstention_slice(self):
        self.assertEqual(abstention_metrics([]),{'correct_abstention':None,'false_abstention':None})
    def test_invalid_claims_and_context(self):
        for claims,context,required in ((CLAIMS,['A','A'],REQUIRED),(CLAIMS,['A'],['status','status']),([dict(CLAIMS[0],cites=['A','A'])],['A'],REQUIRED)):
            with self.assertRaises(ValueError):answer(claims,context,required)

if __name__=='__main__':unittest.main()
