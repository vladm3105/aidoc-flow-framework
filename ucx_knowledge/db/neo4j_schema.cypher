// ============================================================
// PROJECT KNOWLEDGE GRAPH SCHEMA
// Version: 1.0.0
// ============================================================

// ============================================================
// CONSTRAINTS (16 entity types)
// ============================================================

// Market Entities
CREATE CONSTRAINT ticker_symbol IF NOT EXISTS FOR (t:Ticker) REQUIRE t.symbol IS UNIQUE;
CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT sector_name IF NOT EXISTS FOR (s:Sector) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT industry_name IF NOT EXISTS FOR (i:Industry) REQUIRE i.name IS UNIQUE;
CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE;

// Trading Concepts
CREATE CONSTRAINT strategy_name IF NOT EXISTS FOR (s:Strategy) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT structure_name IF NOT EXISTS FOR (s:Structure) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT pattern_name IF NOT EXISTS FOR (p:Pattern) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT bias_name IF NOT EXISTS FOR (b:Bias) REQUIRE b.name IS UNIQUE;
CREATE CONSTRAINT signal_name IF NOT EXISTS FOR (s:Signal) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT risk_name IF NOT EXISTS FOR (r:Risk) REQUIRE r.name IS UNIQUE;

// People
CREATE CONSTRAINT executive_name IF NOT EXISTS FOR (e:Executive) REQUIRE e.name IS UNIQUE;
CREATE CONSTRAINT analyst_name IF NOT EXISTS FOR (a:Analyst) REQUIRE a.name IS UNIQUE;

// Analysis & Learning
CREATE CONSTRAINT analysis_id IF NOT EXISTS FOR (a:Analysis) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT trade_id IF NOT EXISTS FOR (t:Trade) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT learning_id IF NOT EXISTS FOR (l:Learning) REQUIRE l.id IS UNIQUE;

// Provenance
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;

// Time
CREATE CONSTRAINT timeframe_name IF NOT EXISTS FOR (t:Timeframe) REQUIRE t.name IS UNIQUE;

// Metrics
CREATE CONSTRAINT financial_metric_name IF NOT EXISTS FOR (f:FinancialMetric) REQUIRE f.name IS UNIQUE;

// ============================================================
// INDEXES
// ============================================================

// High-traffic lookups
CREATE INDEX ticker_symbol_idx IF NOT EXISTS FOR (t:Ticker) ON (t.symbol);
CREATE INDEX company_name_idx IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX sector_name_idx IF NOT EXISTS FOR (s:Sector) ON (s.name);

// Temporal queries
CREATE INDEX earnings_date_idx IF NOT EXISTS FOR (e:EarningsEvent) ON (e.date);
CREATE INDEX catalyst_date_idx IF NOT EXISTS FOR (c:Catalyst) ON (c.date);
CREATE INDEX analysis_created_idx IF NOT EXISTS FOR (a:Analysis) ON (a.created_at);
CREATE INDEX trade_created_idx IF NOT EXISTS FOR (t:Trade) ON (t.created_at);

// Type-based filtering
CREATE INDEX analysis_type_idx IF NOT EXISTS FOR (a:Analysis) ON (a.type);
CREATE INDEX catalyst_type_idx IF NOT EXISTS FOR (c:Catalyst) ON (c.type);
CREATE INDEX trade_outcome_idx IF NOT EXISTS FOR (t:Trade) ON (t.outcome);
CREATE INDEX learning_category_idx IF NOT EXISTS FOR (l:Learning) ON (l.category);

// Extraction tracking
CREATE INDEX analysis_extract_ver_idx IF NOT EXISTS FOR (a:Analysis) ON (a.extraction_version);

// ============================================================
// FULL-TEXT SEARCH
// ============================================================

CALL db.index.fulltext.createNodeIndex(
  'entitySearch',
  ['Ticker', 'Company', 'Executive', 'Product', 'Pattern', 'Risk', 'Strategy', 'Bias'],
  ['name', 'symbol', 'description']
);

// ============================================================
// RELATIONSHIP TYPES DOCUMENTATION
// ============================================================
// STRUCTURAL (5):
//   (Company)-[:ISSUED]->(Ticker)
//   (Company)-[:IN_SECTOR]->(Sector)
//   (Company)-[:IN_INDUSTRY]->(Industry)
//   (Company)-[:MAKES]->(Product)
//   (Executive)-[:LEADS {title, since}]->(Company)
//
// COMPETITIVE (4):
//   (Company)-[:COMPETES_WITH]->(Company)
//   (Company)-[:SUPPLIES_TO]->(Company)
//   (Company)-[:CUSTOMER_OF]->(Company)
//   (Ticker)-[:CORRELATED_WITH {coefficient, period, calculated_at}]->(Ticker)
//
// TRADING (4):
//   (Strategy)-[:WORKS_FOR {win_rate, sample_size, last_used}]->(Ticker)
//   (Strategy)-[:USES]->(Structure)
//   (Bias)-[:DETECTED_IN {severity, impact_description}]->(Trade)
//   (Pattern)-[:OBSERVED_IN]->(Ticker)
//   (Signal)-[:INDICATES]->(Ticker)
//
// EVENTS (3):
//   (Ticker)-[:HAS_EARNINGS]->(EarningsEvent)
//   (Ticker)-[:AFFECTED_BY]->(Catalyst)
//   (Ticker)-[:EXPOSED_TO]->(MacroEvent)
//   (Risk)-[:THREATENS]->(Ticker)
//
// ANALYSIS (3):
//   (Analysis)-[:ANALYZES]->(Ticker)
//   (Analysis)-[:MENTIONS]->(any entity)
//   (Trade)-[:BASED_ON]->(Analysis)
//   (Trade)-[:TRADED]->(Ticker)
//   (Analyst)-[:COVERS {rating, target_price, updated_at}]->(Ticker)
//
// LEARNING (3):
//   (Learning)-[:DERIVED_FROM]->(Trade)
//   (Learning)-[:ADDRESSES]->(Bias)
//   (Learning)-[:UPDATES]->(Strategy)
//   (Risk)-[:MITIGATED_BY]->(Strategy)
//
// PROVENANCE (1):
//   (any)-[:EXTRACTED_FROM {field_path, confidence, extracted_at}]->(Document)
