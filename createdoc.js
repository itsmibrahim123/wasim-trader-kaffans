const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require('docx');
const fs = require('fs');

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Mubeen Ahmed", bold: true, size: 28 })],
        spacing: { after: 120 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "Roll No: 24U00315", size: 24 })],
        spacing: { after: 480 }
      }),

      new Paragraph({
        children: [new TextRun({ text: "Q1: Impact of Education on Water Consumption and Awareness", bold: true, size: 26 })],
        spacing: { before: 240, after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "The study conducted by Jarad Kinyoun at the University of Nebraska-Lincoln demonstrated that educating households about water scarcity and conservation techniques had a measurable positive impact on both water consumption and overall awareness levels.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "In terms of water consumption, the average monthly usage across participating households decreased from 5.3 units prior to the study to 5.2 units during the study period (January to April 2012), representing an average reduction of 3.2%. Nine out of fourteen households recorded a decrease in water consumption after receiving education. The most notable individual reduction was 38.1% (Household 7), while other households achieved reductions of 25% and 23.2% respectively. Some households showed increased usage, largely attributable to external factors such as changes in the number of residents or installation of new appliances, rather than a failure of the educational intervention.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Regarding awareness, the results were even more striking. A post-study exit survey revealed an overall 27.1% increase in water-related awareness across the six survey questions. The most significant improvement was in participants' knowledge of global water scarcity (Q5), which increased by 60%, followed by awareness of regional water issues (Q4) at 44.1%. Awareness of how much water their household uses monthly (Q2) improved by 25%, comfort with water-saving techniques (Q3) rose by 16.1%, and how much they valued water (Q1) increased by 10%. The least change was in participants' belief about a future global water shortage (Q6), which still rose by 7.4%.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "These findings confirm the study's hypothesis: when individuals are educated on water scarcity issues and conservation techniques, they make choices that lower consumption. The education functioned both consciously and subconsciously, influencing behavioral change even among participants who felt they had already been practicing adequate conservation before the study began.",
          size: 24
        })],
        spacing: { after: 480 }
      }),

      new Paragraph({
        children: [new TextRun({ text: "Q2: Why Individual Behavior and Awareness Are Critical in Addressing Global Water Scarcity", bold: true, size: 26 })],
        spacing: { before: 240, after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "The study argues, both implicitly and explicitly, that individual behavior and awareness are essential components in tackling the global water scarcity crisis. Several interconnected reasons underpin this argument.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "First, the scale of individual consumption is enormous. The average American consumes approximately 2,000 gallons of water per day, with 70% of that used indoors. Nearly 95% of an individual's water footprint is hidden in food, energy, products, and services. Given a global population that reached 7 billion in 2011 and continues to grow, the cumulative impact of individual household usage is staggering. Small reductions at the household level, when multiplied across millions of consumers, translate into significant conservation at regional and global scales.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Second, the study highlights that current water policies are insufficient. Water utilities typically charge only for delivery, failing to account for the true environmental cost of water. Policies do not adequately reflect the value of freshwater or incentivize conservation. In this policy vacuum, individual awareness and voluntary behavioral change become even more critical as a frontline response.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Third, individual-level interventions are practical and low-cost. The study demonstrated that simple actions such as fixing toilet leaks, using toilet banks, and adopting mindful water habits can yield meaningful reductions in consumption. Boston's success story reinforces this point: the city achieved a 43% reduction in peak water use over 30 years through infrastructure upgrades and household-level efficiency improvements, avoiding the need to divert a major river.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Fourth, awareness creates a feedback loop for broader change. As the author notes, awareness leads to change, and change requires knowledge. When individuals understand how their daily habits affect regional and global water availability, they are more likely to adopt conservation behaviors. Moreover, informed citizens are more likely to support water-saving policies and community-level initiatives.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Finally, the study underscores that change can occur even without dramatic lifestyle overhauls. Several households reduced water usage without consciously perceiving major changes in their habits, suggesting that even subtle shifts in awareness can translate into measurable conservation outcomes. The author concludes that marketing campaigns and community education programs have significant potential to reduce freshwater consumption at scale, provided they effectively communicate the urgency and personal relevance of water scarcity.",
          size: 24
        })],
        spacing: { after: 160 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "In sum, the study suggests that addressing global water scarcity cannot rely solely on top-down infrastructure projects or policy mandates. Individual awareness and behavioral change are indispensable, complementary forces that, when mobilized through education and community engagement, can meaningfully contribute to the preservation of freshwater resources for future generations.",
          size: 24
        })],
        spacing: { after: 0 }
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/water_scarcity_answers.docx', buffer);
  console.log('Done');
});